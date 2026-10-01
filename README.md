# KeraNova

Keratoconus research protocol and public-data feasibility resources for the Eye Hackathon. The objective is to develop and evaluate an explainable model that predicts corrected distance visual acuity (CDVA, logMAR) about one year after treatment.

**Current status: the seven protocol documents are completed as research drafts. The institutional prediction model remains untrained. Exploratory public CXL model outputs are present in [KeraNova_Fast_Model/](KeraNova_Fast_Model/); these are separate from the institutional study and do not establish clinical validation or committee approval.** The protocol result tables remain unfilled shells. See [Committee_Readiness.txt](KeraNova_Submission/Committee_Readiness.txt) for the remaining decisions and review limitations. The readiness note and committee ZIP describe the earlier protocol snapshot and do not incorporate the subsequent fast-model experiment.

## Continue on another machine

```sh
git clone https://github.com/mtaher852281/keranova.git
cd keranova
```

Start with this README, [1. Methodology.docx](1.%20Methodology.docx), [6. Statistical_Plan.docx](6.%20Statistical_Plan.docx), and the committee readiness note. Read [AGENTS.md](AGENTS.md) before using a coding agent. Word documents can be read without installing Python.

To rebuild the documents, use Python 3.10 or later:

```sh
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```sh
source .venv/bin/activate
```

Then:

```sh
python -m pip install -r requirements.txt
python scripts/build_protocol.py
```

This writes seven editable DOCX files and `document_manifest.json` into `generated/`. The builder reopens each document, checks basic content, and records SHA-256 hashes. It does not check rendered pagination or train a model. The requirements file covers document generation only.

## Research objective and scope

The institutional study is planned as an exclusively retrospective cohort at King Khaled Eye Specialist Hospital (KKESH), Riyadh, using records from January 2020 to January 2025. The proposed cohort is 60 eligible eyes, ideally 30 treated with topography-guided photorefractive keratectomy plus accelerated corneal cross-linking (TG-PRK + CXL) and 30 with accelerated CXL alone. These are planned counts, not confirmed eligible sample sizes. Exact record-date boundaries and eligibility must be verified with the clinical team.

The primary target is postoperative CDVA in logMAR at the visit closest to the 12-month anniversary within the inclusive 10–14 calendar-month window. If two visits are equally close, select the earlier visit. Baseline measurements must be valid preoperative observations. The documents identify a conflict between the endpoint window and earlier wording requiring at least 12 months of follow-up; the clinical team must resolve that wording before extraction.

The prespecified six predictors are baseline CDVA, age, sex, treatment cohort, maximum keratometry (Kmax), and thinnest corneal thickness (TCT). The initial model is ridge regression, compared with a clinical benchmark using baseline CDVA and treatment cohort. Resampling must group both eyes of a patient together, with preprocessing and predictor imputation fitted only within training folds. Missing outcomes are not imputed. This is a prediction study under observed treatment; a predicted difference between treatment inputs does not establish a causal treatment benefit.

The primary model uses clinical measurements. Corneal images are an optional additional research direction and require a dataset with suitable linked outcome labels; diagnostic images alone do not supply the one-year outcome.

## Completed documents

| File | Purpose |
| --- | --- |
| [1. Methodology.docx](1.%20Methodology.docx) | Objective, design, eligibility, endpoint, model scope and governance |
| [2. Data_Collection_Sheet.docx](2.%20Data_Collection_Sheet.docx) | Blank extraction form with patient/eye linkage, dates, predictors and outcomes |
| [3. Data_Variable_Mapping_Sheet.docx](3.%20Data_Variable_Mapping_Sheet.docx) | Variable definitions, units and source-to-analysis mapping |
| [4. Data_Cleaning_Rules.docx](4.%20Data_Cleaning_Rules.docx) | Missingness, range checks, unresolved anomalies and audit trail |
| [5. Data_Transformation_Template.docx](5.%20Data_Transformation_Template.docx) | Derived fields, acuity conversion, endpoint selection and model input specification |
| [6. Statistical_Plan.docx](6.%20Statistical_Plan.docx) | Cohort description, patient-grouped model evaluation and sensitivity analyses |
| [7. Dummy_Tables_and_Figures.docx](7.%20Dummy_Tables_and_Figures.docx) | Unfilled reporting tables and planned figures; no invented results |

The same seven files appear in [KeraNova_Submission/](KeraNova_Submission/) alongside the readiness note, public dataset search and public-data provenance. [KeraNova_Committee_Package_2026-10-01.zip](KeraNova_Committee_Package_2026-10-01.zip) is the reviewed submission snapshot dated 1 October 2026. Publication on GitHub does not mean submission to, or approval by, the committee.

The previous root templates concerned glaucoma and were replaced with the KeraNova protocol. Their backups are included in [Original_Glaucoma_Templates_2026-10-01/](Original_Glaucoma_Templates_2026-10-01/) as historical material, not the current study protocol. Content review and page-preview checks were performed on the final drafts. Native Word/LibreOffice pagination was unavailable, so opening all seven documents in Word and checking the final page layout remains advisable before submission; details are in the readiness note.

## Institutional dataset: included and incomplete

The original [dataset.csv](dataset.csv) is included at the project owner's explicit request to publish the entire project folder. The audit found 79 eye-like rows plus four administrative rows across 42 columns: 27 labelled PRK+CXL, 51 labelled CXL/CXL-only, and one labelled PTK+CXL. These source labels do not by themselves confirm the specified treatment protocols or eligibility.

Only nine baseline CDVA values and two nominal 12-month CDVA entries were present. One of the two endpoint entries uses qualified Snellen notation and requires adjudication. Patient identifiers, laterality linkage and treatment/visit dates required for the intended analysis were missing. These findings describe data availability; they are not study results and do not support training the proposed model.

To continue the institutional study, obtain the approved, properly linked records through the data custodian and complete the collection sheet. The repository now includes the original [idea/](idea/), [others/](others/), research methodology, workflow image and historical templates. Some original forms contain team or investigator contact details. Inclusion of these originals does not establish ethics approval or permission to obtain additional clinical records. The historical README is retained in the backup directory; this root README is the current continuation guide.

## Public datasets and images

The full candidate review is in [Public_Dataset_Search.txt](KeraNova_Submission/Public_Dataset_Search.txt). No verified public source in that review provides both TG-PRK + accelerated CXL and accelerated CXL-alone cohorts with linked images, all six baseline predictors and a date-qualified one-year CDVA outcome.

### Public CXL outcome data included

The repository includes a coded research derivative of the supplementary dataset from Wajnsztajn et al. (2022):

- [Research derivative CSV](KeraNova_Submission/Public_Data/Wajnsztajn_2022_CXL_research_derivative.csv)
- [Dataset provenance](KeraNova_Submission/Public_Data/Dataset_Provenance.json)
- [Source-file verification](KeraNova_Submission/Public_Data/Source_File_Verification.json)
- [Original article and supplementary files](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0263528)

The source has 613 records representing 456 source patient IDs. There are 336 nominal one-year logMAR outcomes, including 334 baseline/one-year pairs across 251 source patient IDs. These are availability counts before the final eligibility, quality and complete-predictor checks.

The dataset contains conventional and accelerated CXL, with no TG-PRK cohort. Actual treatment/visit dates and eye laterality are absent. One source ID has three records, and 79 last-follow-up durations are negative and need investigation. Its pachymetry is central corneal thickness (CCT), not TCT; the two must not be silently substituted. Consequently, a model using these data would be a separately specified public CXL feasibility experiment with a nominal one-year target, not validation of the institutional protocol or its treatment comparison.

Original public-source downloads and metadata are also included in [Public_Datasets/](Public_Datasets/). They retain source fields that were removed or recoded in the research derivative; use the coded derivative for the documented feasibility workflow.

**Attribution and licence:** © 2022 Wajnsztajn et al. Wajnsztajn D, Shmueli O, Zur K, Frucht-Pery J, Solomon A (2022), PLOS ONE article DOI [10.1371/journal.pone.0263528](https://doi.org/10.1371/journal.pone.0263528), S1 Data DOI [10.1371/journal.pone.0263528.s005](https://doi.org/10.1371/journal.pone.0263528.s005). The source is published under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). This derivative selects research columns, removes original patient IDs/file numbers, substitutes `PLSP` patient codes and `PLSR` record codes, and normalizes whitespace/missing-value strings. All 613 records are retained; inclusion in this file is not a declaration of analytical eligibility. Retain this attribution and disclose further changes when redistributing.

### Public corneal images identified

[CornOrb on Zenodo](https://zenodo.org/records/20542091) reports 1,454 examinations from 744 patients, four corneal maps per examination and accompanying tabular data. It is relevant to diagnostic image research, but does not provide the required postoperative CDVA outcome. Its approximately 680 MB archive was not downloaded or added to this repository. The Zenodo record and associated publication show different licence statements (CC BY 4.0 versus CC BY-NC 4.0); clarify the applicable terms before reuse.

The candidate memo also discusses the Aslan CXL dataset, CADMUS, Pentacam diagnostic data and a small CASIA sample. Keep diagnosis, outcome prediction and treatment-effect estimation distinct when selecting a dataset.

## Exploratory public model files

[KeraNova_Fast_Model/](KeraNova_Fast_Model/) contains the analysis cohort, screening ledger, held-out predictions, ridge model parameters and [quick_report.json](KeraNova_Fast_Model/quick_report.json). The training script is [_keranova_build/train_fast_model.py](_keranova_build/train_fast_model.py). Its report describes 314 records from 235 source patients and repeated patient-grouped internal evaluation. These outputs have not been independently validated as part of this publication step. They use a nominal one-year target, heterogeneous correction methods and CCT, with no TG-PRK cohort; the institutional model remains untrained.

The report records Python 3.12.14, NumPy 2.3.5 and pandas 3.0.1. Those model dependencies are separate from the document-builder requirements. Do not merge these exploratory metrics into institutional result tables or describe them as external validation.

## Editing and maintaining the package

- [protocol_sources/methods_statistics.json](protocol_sources/methods_statistics.json) contains the reviewed content for documents 1, 6 and 7.
- [protocol_sources/data_workflow.json](protocol_sources/data_workflow.json) contains the reviewed content for documents 2–5.
- [scripts/build_protocol.py](scripts/build_protocol.py) turns those sources into editable Word documents with consistent layout.

Use the JSON sources for lasting content changes, then rebuild. If a document is edited directly in Word, incorporate those changes into its JSON source before the next build. The document version/date banner is currently fixed to version 1.0 / 1 October 2026 in the builder and must be updated for a new release.

A custom build directory is supported:

```sh
python scripts/build_protocol.py --output-dir generated/review
```

After content review, render or open every page and check tables, headings, page breaks and reference links. Only then promote the reviewed files to both the root and `KeraNova_Submission/`, and recreate the committee ZIP. The builder intentionally leaves the published submission snapshot untouched by default. Keep both document locations and the ZIP synchronized for each release.

## Next work

1. Resolve clinical definitions, exact extraction dates, endpoint wording, IRB status and permitted use with the research team.
2. Choose either the authorized institutional extraction or a separately labelled public CXL feasibility experiment. They have different cohort coverage and available measurements.
3. Audit patient linkage, adult eligibility, source anomalies, predictor completeness, acuity units and usable outcomes before choosing any model split.
4. Independently review the public fast-model pipeline and its outputs before extending them. Implement the institutional patient-grouped pipeline with training-fold-only transformations, the clinical benchmark, ridge regression, uncertainty estimates and prespecified evaluation metrics when suitable institutional records are available.
5. Fill the reporting shells only with verified outputs, and state feasibility limits when the sample cannot support the planned evaluation.
6. Have the clinical team review the protocol and final Word layout before submitting the package.

A useful continuation prompt is: "Read the KeraNova README, readiness note, documents 1, 5 and 6, and KeraNova_Fast_Model/quick_report.json. The institutional model remains untrained. Review the exploratory public CXL experiment and its eligibility/completeness audit, respecting patient grouping, its nominal one-year outcome and CCT/TCT distinction. Keep that feasibility experiment separate from the institutional protocol."

## Public repository boundaries

The project owner explicitly requested publication of the entire folder, including `dataset.csv` and the source materials. Project files, historical backups, generated previews, local build scripts, downloaded dependencies and coding-tool configuration are included. `.gitignore` excludes Git internals, the rebuildable `.code-review-graph/` cache and credential-file patterns. No credentials were found in the scanned project files. Do not add new credentials or newly obtained identifiable clinical records to this public repository.

Dataset licences apply to their respective sources; public availability of this repository does not grant additional rights to institutional data or third-party materials.
