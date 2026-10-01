"""Inspect public KeraNova candidate files without printing individual records.

The script reads the preserved XLSX and SAV sources, writes aggregate schema
evidence to JSON, and does not modify the sources. File and parser errors propagate.
"""

import hashlib
import json
import sys
from collections import Counter
import csv
import math
from pathlib import Path

import openpyxl

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "_keranova_build" / "public_read_deps"))
import pyreadstat


def fingerprint(path: Path) -> dict:
    """Return byte count and SHA256 for path; raise OSError on unreadable files."""
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def inspect_excel(path: Path) -> dict:
    """Return worksheet headers and completeness counts for an XLSX source.

    Args: path: Preserved public workbook.
    Returns: Aggregate sheet metadata without patient records.
    Raises: OSError or openpyxl parser errors when the workbook cannot be read.
    Side effects: None. The workbook is opened in read-only mode.
    """
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = []
    for sheet in workbook:
        rows = list(sheet.iter_rows(values_only=True))
        headers = [str(value) if value is not None else "" for value in rows[0]]
        data = [row for row in rows[1:] if any(value is not None for value in row)]
        counts = {str(index + 1) + ":" + header: sum(row[index] is not None for row in data)
                  for index, header in enumerate(headers)}
        selected = ["number", "file number", "ID", "AGE", "SEX", "Pachymetry",
                    "K Max Pre", "LogMAR Pre", "LogMAR 1Y", "LogMar, last measurement",
                    "CXL non-accelerated(0) Vs. accelerated(1)", "FU time months"]
        distributions = {header: field_summary([row[headers.index(header)] for row in data],
                                              identifier=header in {"number", "file number", "ID"})
                         for header in selected if header in headers}
        paired = sum(is_numeric(row[headers.index("LogMAR Pre")]) and
                     is_numeric(row[headers.index("LogMAR 1Y")]) for row in data)
        sheets.append({"name": sheet.title, "max_rows": sheet.max_row,
                       "max_columns": sheet.max_column, "nonempty_data_rows": len(data),
                       "headers": headers, "nonmissing_counts": counts,
                       "selected_field_summary": distributions,
                       "numeric_baseline_and_1year_logmar_pairs": paired})
    workbook.close()
    return {**fingerprint(path), "sheets": sheets}


def inspect_spss(path: Path) -> dict:
    """Return SAV labels and completeness counts without individual records.

    Args: path: Preserved public SPSS source.
    Returns: Aggregate schema and number of observations.
    Raises: OSError or ReadstatError if unreadable.
    Side effects: None; sources remain unchanged.
    """
    frame, metadata = pyreadstat.read_sav(str(path))
    return {**fingerprint(path), "rows": len(frame), "columns": len(frame.columns),
            "labels": metadata.column_names_to_labels,
            "value_labels": metadata.variable_value_labels,
            "nonmissing_counts": frame.notna().sum().to_dict(),
            "group_counts": frame["Group"].value_counts().to_dict(),
            "followup_counts": frame["FOLLOWUP"].value_counts().to_dict(),
            "eye_field_distinct": int(frame["Eye"].nunique()),
            "duplicate_rows": int(frame.duplicated().sum()),
            "field_ranges": {field: {"min": float(frame[field].min()),
                                      "max": float(frame[field].max())}
                             for field in ["Age", "LOGVAPRE", "LOGVAPOST", "KMAXPRE", "THICKPRE"]}}


def is_numeric(value) -> bool:
    """Return whether value is a real number, excluding bool; raise no expected errors."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def field_summary(values: list, identifier: bool = False) -> dict:
    """Summarize numeric availability and missing sentinels; do not print identifiers.

    Args: values: One source field's values. identifier: Suppress identifier examples/ranges.
    Returns: Numeric count/range, distinct count and common nonnumeric markers.
    Raises: TypeError for unexpected nonhashable values.
    Side effects: None.
    """
    numbers = [value for value in values if is_numeric(value)]
    markers = Counter(str(value) for value in values if not is_numeric(value))
    return {"numeric_count": len(numbers), "distinct_nonblank_values": len(set(values) - {None, "", "."}),
            "numeric_min": min(numbers) if numbers and not identifier else None,
            "numeric_max": max(numbers) if numbers and not identifier else None,
            "nonnumeric_markers": dict(markers.most_common(3)) if not identifier else {}}


def create_plos_derivative(path: Path, target: Path) -> dict:
    """Write a CSV research derivative with pseudonymous study keys and numeric fields.

    Args: path: Preserved PLOS workbook. target: Derived CSV path.
    Returns: Availability, linkage and nominal one-year endpoint checks.
    Raises: OSError, parser errors, or ValueError for inconsistent workbook linkage.
    Side effects: Writes target CSV; never changes path; does not export original IDs/file numbers.
    """
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    coded_rows = list(workbook["codes"].iter_rows(values_only=True))
    label_rows = list(workbook["Labels"].iter_rows(values_only=True))
    headers, labels = list(coded_rows[0]), list(label_rows[0])
    data = [dict(zip(headers, row)) for row in coded_rows[1:]]
    label_data = [dict(zip(labels, row)) for row in label_rows[1:]]
    workbook.close()
    if [row["number"] for row in data] != [row["number"] for row in label_data]:
        raise ValueError("codes and Labels worksheets are not aligned by number")
    patient_codes = {identifier: f"PLSP{index + 1:04d}"
                     for index, identifier in enumerate(dict.fromkeys(row["ID"] for row in data))}
    mapping = {"age_years": "AGE", "sex_source_code": "SEX", "pachymetry_um": "Pachymetry",
               "baseline_kmax_d": "K Max Pre", "baseline_mean_k_d": "Mean K/Pre",
               "baseline_spherical_equivalent_d": "SE Pre", "baseline_cylinder_d": "Cyl pre",
               "cxl_accelerated_source_code": "CXL non-accelerated(0) Vs. accelerated(1)",
               "baseline_cdva_logmar": "LogMAR Pre", "nominal_1year_cdva_logmar": "LogMAR 1Y",
               "nominal_1year_kmax_d": "Kmax1y", "last_cdva_logmar": "LogMar, last measurement",
               "source_last_followup_months": "FU time months"}
    derivatives = [make_derivative(row, label, patient_codes, mapping, index)
                   for index, (row, label) in enumerate(zip(data, label_data), start=1)]
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(derivatives[0]))
        writer.writeheader()
        writer.writerows(derivatives)
    patient_counts = Counter(row["ID"] for row in data)
    target_rows = [row for row in derivatives if row["nominal_1year_cdva_logmar"] != ""]
    pair_rows = [row for row in target_rows if row["baseline_cdva_logmar"] != ""]
    conversions = [abs(row["LogMAR 1Y"] + math.log10(row["BCVA 1Y"]))
                   for row in data if is_numeric(row["LogMAR 1Y"]) and
                   is_numeric(row["BCVA 1Y"]) and row["BCVA 1Y"] > 0]
    fu_values = [row["FU time months"] for row in data if is_numeric(row["FU time months"])]
    return {**fingerprint(target), "rows": len(data), "patients": len(patient_codes),
            "nominal_1year_cdva_numeric": len(target_rows), "baseline_and_1year_pairs": len(pair_rows),
            "patients_with_nominal_1year_cdva": len({row["study_patient_id"] for row in target_rows}),
            "patients_with_baseline_and_1year_pairs": len({row["study_patient_id"] for row in pair_rows}),
            "maximum_source_rows_per_patient": max(patient_counts.values()),
            "patients_with_more_than_two_source_rows": sum(count > 2 for count in patient_counts.values()),
            "paired_acceleration_counts": dict(Counter(row["cxl_accelerated_source_code"] for row in pair_rows)),
            "nominal_1year_bcva_logmar_conversion_pairs": len(conversions),
            "nominal_1year_conversion_mismatches_tolerance_0_000001": sum(value > 1e-6 for value in conversions),
            "negative_last_followup_count": sum(value < 0 for value in fu_values),
            "nominal_1year_calendar_window_verified": False,
            "laterality_available": False}


def make_derivative(row: dict, label: dict, patient_codes: dict, mapping: dict, index: int) -> dict:
    """Return one pseudonymous numeric CSV row; args are source maps/key lookup/ordinal.

    Returns: Research row with explicit nominal endpoint and unresolved quality flags.
    Raises: KeyError on an inconsistent source schema. Side effects: None.
    """
    result = {"study_record_id": f"PLSR{index:04d}", "study_patient_id": patient_codes[row["ID"]]}
    result.update({name: row[source] if is_numeric(row[source]) else "" for name, source in mapping.items()})
    result.update({"sex_label": label["SEX"], "epithelium_label": label["epithel off \\ on"],
                   "correction_before_label": label["Correction before"], "source_visit_label": "1Y",
                   "visit_dates_available": False, "window_10_14_months_verified": False})
    return result


def main() -> None:
    """Write aggregate public-file evidence; return None; propagate parser/I/O errors."""
    sources = BASE / "Public_Datasets"
    report = {"checked_date": "2026-10-01",
              "plos": inspect_excel(sources / "Wajnsztajn_2022_CXL_raw.xlsx"),
              "mendeley": inspect_spss(sources / "Aslan_2020_A_TE_CXL_HCL_raw.sav"),
              "plos_derivative": create_plos_derivative(sources / "Wajnsztajn_2022_CXL_raw.xlsx",
                                                        sources / "Wajnsztajn_2022_CXL_research_derivative.csv")}
    target = BASE / "_keranova_build" / "public_data_file_audit.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
