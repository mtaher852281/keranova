"""Run a fast, patient-grouped public CXL outcome prediction experiment.

Uses five preoperative predictors, nested ridge tuning, and matched clinical
and mean benchmarks. This is a separate nominal-one-year feasibility study;
it does not train on KKESH data or implement the protocol's full bootstrap CIs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Public_Datasets" / "Wajnsztajn_2022_CXL_research_derivative.csv"
OUTPUT = ROOT / "KeraNova_Fast_Model"
FEATURES = ["baseline_cdva_logmar", "age_years", "sex_source_code",
            "baseline_kmax_d", "pachymetry_um"]
TARGET = "nominal_1year_cdva_logmar"
GRID = np.array([0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
SEED = 20261001
REPEATS = 20


def prepare_data() -> tuple[pd.DataFrame, dict]:
    """Screen complete records and known unresolved source quality flags.

    Returns:
        Screened records and mutually exclusive exclusion counts.
    Raises:
        ValueError: If the screened sample lacks adequate grouping or variation.
    Side effects:
        Writes a coded screening ledger; source CSV remains unchanged.
    """
    data = pd.read_csv(SOURCE)
    count = data.groupby("study_patient_id")["study_record_id"].transform("size")
    reason = pd.Series("included", index=data.index)
    reason.loc[count > 2] = "source patient has more than two records"
    eligible = reason == "included"
    reason.loc[eligible & (data["source_last_followup_months"] < 0)] = "negative source last-followup metadata"
    eligible = reason == "included"
    reason.loc[eligible & (data["age_years"] < 18)] = "age below 18"
    eligible = reason == "included"
    reason.loc[eligible & data[TARGET].isna()] = "missing nominal one-year outcome"
    eligible = reason == "included"
    reason.loc[eligible & data[FEATURES].isna().any(axis=1)] = "missing baseline predictor"
    data["screening_disposition"] = reason
    data.to_csv(OUTPUT / "screening_ledger.csv", index=False)
    cohort = data.loc[reason == "included"].copy().reset_index(drop=True)
    numeric = cohort[FEATURES + [TARGET]].to_numpy(float)
    if not np.isfinite(numeric).all() or cohort["study_patient_id"].nunique() < 25:
        raise ValueError("Sample is not suitable for the planned grouped folds")
    if cohort[TARGET].std() == 0 or set(cohort["sex_source_code"]) != {0, 1}:
        raise ValueError("Required outcome or sex variation is absent")
    audit = {"source_rows": len(data), "source_patients": data["study_patient_id"].nunique(),
             "screening_counts": reason.value_counts().to_dict(), "analysis_records": len(cohort),
             "analysis_patients": cohort["study_patient_id"].nunique(),
             "cxl_protocol_counts": cohort["cxl_accelerated_source_code"].value_counts().to_dict(),
             "baseline_correction_labels": cohort["correction_before_label"].fillna("unknown").value_counts().to_dict()}
    return cohort, audit


def grouped_folds(groups: np.ndarray, count: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """Make reproducible disjoint-patient training/test index pairs.

    Args:
        groups: Patient code for each observation.
        count: Number of folds.
        seed: Random seed for shuffling unique patients.
    Returns:
        Training/test row indices for every fold.
    Raises:
        ValueError: If there are fewer patients than folds.
    """
    patients = np.unique(groups)
    if len(patients) < count:
        raise ValueError("Too few independent patients")
    patients = np.random.default_rng(seed).permutation(patients)
    partitions = np.array_split(patients, count)
    folds = []
    for patients_in_test in partitions:
        test_mask = np.isin(groups, patients_in_test)
        train, test = np.flatnonzero(~test_mask), np.flatnonzero(test_mask)
        assert not set(groups[train]).intersection(groups[test])
        folds.append((train, test))
    return folds


def fit_ridge(x: np.ndarray, y: np.ndarray, penalty: float) -> dict:
    """Fit training-only standardized ridge with an unpenalized intercept.

    Args:
        x: Five-column baseline training matrix.
        y: Training outcome vector.
        penalty: Lambda in mean-square-error plus lambda times squared slopes.
    Returns:
        Scaling constants and fitted standardized coefficients.
    Raises:
        numpy.linalg.LinAlgError: If the regularized linear system fails.
    """
    means, scales = x.mean(axis=0), x.std(axis=0)
    means[2], scales[2] = 0.0, 1.0  # Retain sex coding rather than standardizing.
    scales[scales == 0] = 1.0
    design = np.column_stack([np.ones(len(x)), (x - means) / scales])
    regularizer = np.diag([0.0] + [penalty] * len(FEATURES))
    coefficients = np.linalg.solve(design.T @ design / len(x) + regularizer,
                                   design.T @ y / len(x))
    return {"means": means, "scales": scales, "coefficients": coefficients, "lambda": penalty}


def predict(model: dict, x: np.ndarray) -> np.ndarray:
    """Apply a training-fitted ridge transform and coefficients.

    Args:
        model: Fitted ridge parameters.
        x: Baseline matrix in the same feature order.
    Returns:
        Predicted nominal-one-year corrected vision in logMAR.
    """
    design = np.column_stack([np.ones(len(x)), (x - model["means"]) / model["scales"]])
    return design @ model["coefficients"]


def choose_penalty(x: np.ndarray, y: np.ndarray, groups: np.ndarray, seed: int) -> float:
    """Select lambda using pooled four-fold inner held-out MAE only.

    Args:
        x: Outer-training baseline data.
        y: Outer-training outcomes.
        groups: Outer-training patient IDs.
        seed: Inner fold seed.
    Returns:
        Selected lambda; exact-score ties favour the larger lambda.
    """
    folds = grouped_folds(groups, 4, seed)
    best_score, selected = float("inf"), float(GRID[0])
    for penalty in GRID:
        predictions = np.empty(len(y))
        for train, test in folds:
            predictions[test] = predict(fit_ridge(x[train], y[train], float(penalty)), x[test])
        score = float(np.mean(np.abs(y - predictions)))
        if score <= best_score + 1e-12:
            best_score, selected = score, float(penalty)
    return selected


def metrics(y: np.ndarray, predictions: np.ndarray) -> dict:
    """Calculate continuous-outcome errors, calibration and tolerance fractions.

    Args:
        y: Observed held-out outcomes.
        predictions: Matched held-out predictions.
    Returns:
        Regression metrics; tolerance fractions are not classification accuracy.
    """
    error = predictions - y
    variance = np.sum((y - y.mean()) ** 2)
    calibration = np.linalg.lstsq(np.column_stack([np.ones(len(y)), predictions]), y, rcond=None)[0]
    return {"mae_logmar": float(np.mean(np.abs(error))),
            "rmse_logmar": float(np.sqrt(np.mean(error ** 2))),
            "r_squared": float(1 - np.sum(error ** 2) / variance),
            "mean_prediction_error_logmar": float(error.mean()),
            "calibration_intercept": float(calibration[0]), "calibration_slope": float(calibration[1]),
            "fraction_within_0_10_logmar": float(np.mean(np.abs(error) <= 0.10)),
            "fraction_within_0_20_logmar": float(np.mean(np.abs(error) <= 0.20))}


def clinical_predictions(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray) -> np.ndarray:
    """Fit and apply the baseline-CDVA-only clinical benchmark.

    Args:
        x_train: Training baseline matrix.
        y_train: Training labels.
        x_test: Held-out baseline matrix.
    Returns:
        OLS benchmark predictions using baseline CDVA only.
    """
    coefficients = np.linalg.lstsq(np.column_stack([np.ones(len(x_train)), x_train[:, 0]]),
                                    y_train, rcond=None)[0]
    return np.column_stack([np.ones(len(x_test)), x_test[:, 0]]) @ coefficients


def evaluate(cohort: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Run twenty repeats of grouped five-fold outer/four-fold inner evaluation.

    Args:
        cohort: Screened source records with complete predictors and outcome.
    Returns:
        Mean repeat-level metrics and per-record held-out predictions/folds.
    """
    x, y = cohort[FEATURES].to_numpy(float), cohort[TARGET].to_numpy(float)
    groups = cohort["study_patient_id"].to_numpy()
    rows, summaries = [], {name: [] for name in ("ridge", "baseline_cdva_only", "training_mean")}
    for repeat in range(REPEATS):
        result = {name: np.empty(len(y)) for name in summaries}
        for fold, (train, test) in enumerate(grouped_folds(groups, 5, SEED + repeat)):
            penalty = choose_penalty(x[train], y[train], groups[train], SEED + repeat * 100 + fold + 5000)
            result["ridge"][test] = predict(fit_ridge(x[train], y[train], penalty), x[test])
            result["baseline_cdva_only"][test] = clinical_predictions(x[train], y[train], x[test])
            result["training_mean"][test] = y[train].mean()
            rows.extend(prediction_rows(cohort, test, result, repeat, fold, penalty))
        for name, predictions in result.items():
            summaries[name].append(metrics(y, predictions))
    averaged = {name: {key: float(np.mean([item[key] for item in values]))
                       for key in values[0]} for name, values in summaries.items()}
    averaged["repeat_mae_ranges"] = {name: [min(item["mae_logmar"] for item in values),
                                          max(item["mae_logmar"] for item in values)]
                                    for name, values in summaries.items()}
    return averaged, pd.DataFrame(rows)


def prediction_rows(cohort: pd.DataFrame, test: np.ndarray, predictions: dict,
                    repeat: int, fold: int, penalty: float) -> list[dict]:
    """Format one outer test partition's coded predictions for verification.

    Args:
        cohort: Screened records.
        test: Held-out row indices.
        predictions: Per-model prediction arrays populated at test indices.
        repeat: Repeat index.
        fold: Outer fold index.
        penalty: Inner-selected lambda.
    Returns:
        Prediction records with coded IDs and reproducible fold assignment.
    """
    records = []
    for index in test:
        row = cohort.iloc[index]
        records.append({"study_record_id": row["study_record_id"], "study_patient_id": row["study_patient_id"],
                        "repeat": repeat + 1, "fold": fold + 1, "inner_selected_lambda": penalty,
                        "observed_logmar": row[TARGET],
                        **{name + "_prediction": values[index] for name, values in predictions.items()}})
    return records


def save_model(cohort: pd.DataFrame) -> None:
    """Fit final demonstration parameters after evaluation and save portable JSON.

    Args:
        cohort: Entire screened development sample.
    Returns:
        None. Saves coefficients/scaling; this fit creates no new validation score.
    """
    x, y = cohort[FEATURES].to_numpy(float), cohort[TARGET].to_numpy(float)
    penalty = choose_penalty(x, y, cohort["study_patient_id"].to_numpy(), SEED + 90000)
    model = fit_ridge(x, y, penalty)
    saved = {key: value.tolist() if isinstance(value, np.ndarray) else value for key, value in model.items()}
    saved.update({"feature_order": FEATURES, "target": TARGET, "sex_coding": "male=1,female=0",
                  "scope": "Public CXL-only nominal-one-year feasibility; no clinical treatment recommendation",
                  "prediction_formula": "[1, (x-means)/scales] dot coefficients"})
    (OUTPUT / "ridge_model.json").write_text(json.dumps(saved, indent=2), encoding="utf-8")


def main() -> None:
    """Screen, evaluate, fit and save the fast exploratory experiment.

    Returns:
        None. Writes model, report, cohort, ledger and held-out predictions.
    Raises:
        ValueError, OSError or linear algebra errors on invalid data or I/O.
    """
    start = time.perf_counter()
    OUTPUT.mkdir(exist_ok=True)
    cohort, audit = prepare_data()
    results, predictions = evaluate(cohort)
    save_model(cohort)
    cohort.to_csv(OUTPUT / "analysis_cohort.csv", index=False)
    predictions.to_csv(OUTPUT / "held_out_predictions.csv", index=False)
    report = {"experiment": "Fast public CXL-only nominal-one-year vision prediction", "date": "2026-10-01",
              "source_url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263528",
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "features": FEATURES,
              "screening": audit, "validation": "20 repeats: 5 outer and 4 inner patient-grouped folds",
              "random_seed": SEED, "metrics": results, "bootstrap_confidence_intervals": "Not run in this fast experiment",
              "limitations": ["Nominal one-year label; actual visit dates and laterality absent",
                              "Source correction methods heterogeneous; not harmonized to verified spectacle CDVA",
                              "Public CXL-only sample has no TG-PRK cohort; institutional model remains untrained",
                              "Repeated internal validation is not external validation or clinical approval"],
              "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
              "elapsed_seconds": time.perf_counter() - start}
    (OUTPUT / "quick_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
