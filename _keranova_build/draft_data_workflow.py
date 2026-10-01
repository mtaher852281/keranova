"""Write four KeraNova data-workflow document specifications from audited sources."""

import json
from pathlib import Path

BUILD = Path(r"C:\Users\user\Desktop\Hackathon\_keranova_build")
AUDIT = json.loads((BUILD / "data_audit.json").read_text(encoding="utf-8"))
VERSION = "Version 1.0 for committee review on 1 October 2026"


def section(heading: str, paragraphs: list[str] | None = None, rows: list[list[str]] | None = None, headers: list[str] | None = None, bullets: list[str] | None = None) -> dict:
    """Return a document section specification with optional prose, table and bullets."""
    result = {"heading": heading, "paragraphs": paragraphs or []}
    if rows is not None:
        result["table"] = {"headers": headers, "rows": rows}
    if bullets:
        result["bullets"] = bullets
    return result


def collection_document() -> dict:
    """Return the completed operational collection-form specification for document 2."""
    sections = [section("Purpose and use", [
        "This form supports KeraNova, a retrospective keratoconus study and exploratory prediction of twelve-month corrected distance visual acuity (CDVA). Complete one eye treatment record and repeat the visit form for every relevant visit. An empty entry space is intended for data collection; it is not a patient result.",
        "Use coded patient IDs in the analytic file. The authorized institutional custodian maintains the linkage to source records separately. The index treatment is TG-PRK plus accelerated corneal cross-linking (CXL), or accelerated CXL alone, documented during the parent study period. The intended cohort is up to 60 eligible eyes with 30 per group. Verify the actual cohort before reporting its size.",
        "Record the original measurement and its method before conversion. Use ND for not documented, NA for not applicable, UNK for explicitly unknown, NR for a source that cannot be retrieved, and AMBIG for an unresolved meaning or conflict. Zero and No are observed values. Do not fill missing CDVA from uncorrected or pinhole vision."
    ])]
    sections.append(section("Record identity and source", rows=[
        ["Coded patient ID", "________________", "Stable across both eyes and visits"],
        ["Eye record ID and index episode ID", "________________", "Unique eye and treatment episode"],
        ["Laterality", "OD / OS / UNK", "Right or left from source"],
        ["Age at index treatment", "____ completed years", "Date of birth and index date checked locally; no birth date in analytic export"],
        ["Sex as documented", "Male / Female / Other recorded / UNK", "Do not infer from name"],
        ["Source reference and extraction date", "________________", "File hash, source row or coded record and YYYY-MM-DD"],
        ["Extractor and reviewer codes", "________________", "Coded staff identifiers"],
        ["Index treatment date", "YYYY-MM-DD __________", "Operative record"],
        ["Final eligibility status and reason", "Eligible / Excluded / Pending", "Record each reason and supporting source"]
    ], headers=["Field", "Entry", "Required evidence"]))
    sections.append(section("Eligibility screening", [
        "Complete every criterion from dated source records. Do not infer progression or a contraindication from a single topographic measurement. The clinical lead must confirm the operational progression definition and procedure-specific thickness safety criterion before cohort selection. A missing criterion remains pending."
    ], rows=[
        ["Age at treatment at least 18 years", "Yes / No / UNK", "Verified age at index procedure"],
        ["Progressive keratoconus documented", "Yes / No / UNK", "Progression definition, dates and findings: __________"],
        ["Adequate corneal thickness for received procedure", "Yes / No / UNK", "Metric, measured thickness, criterion and clinical review: __________"],
        ["No prior corneal surgery", "Yes / No / UNK", "History and dated procedure records"],
        ["No CXL contraindication", "Yes / No / UNK", "Clinical assessment and relevant history"],
        ["Index treatment within approved study period", "Yes / No / UNK", "Parent protocol January 2020 to January 2025; verify exact approved boundary dates"],
        ["Procedure matches a study cohort", "Yes / No / UNK", "TG-PRK plus accelerated CXL or accelerated CXL alone"],
        ["Baseline and twelve-month outcome available", "Yes / No / UNK", "Record separately from core clinical eligibility; missing label excludes prediction analysis"]
    ], headers=["Criterion", "Assessment", "Evidence to record"]))
    sections.append(section("Baseline clinical measurements", [
        "Use the nearest valid preoperative measurement for the index eye and preserve each measurement date. A same-day value is baseline only if the source establishes that it was measured before treatment. Record how far each measure precedes the operation and clinically review distant baseline values. Any sensitivity analysis restricting this interval must be prespecified before analysis."
    ], rows=[
        ["Visit date and time if available", "YYYY-MM-DD __________", "Preoperative chronology verified Yes / No / UNK"],
        ["CDVA original notation", "________________", "Chart type, testing distance and correction method: __________"],
        ["CDVA standardized value", "____ logMAR / missing code", "Conversion method and reviewer: __________"],
        ["UDVA original and logMAR", "________________", "Uncorrected distance vision kept separate"],
        ["Manifest sphere and cylinder", "____ D and ____ D", "Minus or plus cylinder convention: __________"],
        ["Cylinder axis and MRSE", "____ degrees; ____ D", "MRSE original and calculated separately"],
        ["K1 and K2", "____ D; ____ D", "Dated device report and scan quality"],
        ["Kmax", "____ D", "Primary candidate predictor"],
        ["Thinnest corneal thickness TCT", "____ micrometres", "Prespecified pachymetry candidate; distinguish from central or apical thickness"],
        ["BAD-D and Amsler Krumeich stage", "________________", "Only verified device score and documented stage"],
        ["Prior surgery, scar and other ocular disease", "________________", "Presence, laterality and dated clinical description"]
    ], headers=["Measurement", "Entry", "Method and quality"]))
    sections.append(section("Index treatment details", rows=[
        ["Procedure as written in record", "________________", "Keep exact source phrase"],
        ["Topography guided PRK verified", "Yes / No / UNK", "Operative or laser treatment report"],
        ["Accelerated CXL verified", "Yes / No / UNK", "Operative report and irradiation protocol"],
        ["Final study group", "TG-PRK plus accelerated CXL / accelerated CXL alone / Other / Pending", "Clinical reviewer code: __________"],
        ["CXL protocol", "________________", "Irradiance, duration, fluence, epithelial status and riboflavin if recorded"],
        ["PRK protocol", "________________", "Ablation depth, optical zone and relevant adjuncts if recorded"],
        ["Additional procedure or deviation", "________________", "PTK and other procedures cannot silently enter either primary group"]
    ], headers=["Field", "Entry", "Source requirement"]))
    sections.append(section("Repeatable follow up visit form", [
        "Capture all relevant visits with actual dates. One- and six-month source labels are interim descriptive information until dates are verified. The primary endpoint is the valid CDVA visit closest to the twelve-month anniversary between the tenth- and fourteenth-month anniversaries, inclusive. Break equal date-distance ties by choosing the earlier visit. Never select a visit because it has better vision."
    ], rows=[
        ["Visit ID and actual date", "________________", "YYYY-MM-DD and source reference"],
        ["Source interval label and elapsed days", "________________", "Retain label separately from date-based selection"],
        ["CDVA original and standardized", "________________", "Chart, correction, modifiers and logMAR"],
        ["UDVA original and standardized", "________________", "Separate measurement and method"],
        ["Sphere, cylinder, axis, MRSE", "________________", "D, D, degrees, D; same encounter"],
        ["K1, K2, Kmax and TCT", "________________", "D, D, D, micrometres; dated scan"],
        ["Haze and other complications", "Yes / No / UNK; description __________", "Grade scale, presence, location, onset and interventions"],
        ["Repeat procedure or new ocular event", "________________", "Type, date and relation to index eye"],
        ["Endpoint selected", "Yes / No / Pending", "Reason, anniversary distance, quality and missing code"]
    ], headers=["Field", "Entry", "Required context"]))
    sections.append(section("Optional imaging and extended Pentacam data", [
        "Images are an optional linked research resource. Record a coded image ID, patient ID, laterality, scan date, preoperative or postoperative status, modality, device and software version, map type, scale, units, scan-quality flag and permitted use. Remove identifiers in metadata and burned-in pixels before an authorized export. Keep original scan metadata locally and preserve a transformation log.",
        "The supplied CSV contains no images or imaging references. Public images cannot supply this cohort's missing postoperative CDVA. Image-based experiments require a separate objective, compatible labels and patient-level splitting; they must not be presented as validation of the twelve-month prediction model.",
        "The header-only research workbook proposes extended fields such as corneal indices, aberrometry and densitometry. Collect these when available and verified, but they are not additional predictors in the primary prespecified model."
    ]))
    sections.append(section("Review and release", bullets=[
        "Check every treatment assignment, clinical eligibility decision and primary CDVA label against the source with a second reviewer.",
        "Record each unresolved issue, requested source, reviewer decision and date. Freeze cohort and dictionary versions before statistical modeling.",
        "Reconcile screened eye records, unique patients, exclusions, pending records and analysis denominators. Signatures: extractor __________ clinical reviewer __________ data custodian __________ date __________."
    ]))
    return {"number": 2, "title": "KeraNova Data Collection Sheet", "subtitle": VERSION, "sections": sections}


def mapped_rows(specs: list[tuple[int, str, str]]) -> list[list[str]]:
    """Return exact CSV header mapping rows for one-based column specifications."""
    return [[str(col), AUDIT["csv"]["headers"][col-1]["escaped_header"], field, rule] for col,field,rule in specs]


def mapping_document() -> dict:
    """Return source-specific and intended-schema mapping specification for document 3."""
    heads = ["CSV column", "Exact source header", "Clean field and unit", "Interpretation and rule"]
    sections = [section("Scope and source authority", [
        "This dictionary maps all 42 columns of dataset.csv and defines the additional fields required by KeraNova. Quoted source headers preserve leading and trailing spaces; the quotation marks are notation, not part of the header. Column numbers are one-based. Do not rename source headers in place. Assign unique clean field names in a derivative table.",
        "The CSV has 79 eye-record rows and four section-heading rows. A source row is a record identifier, not a patient identifier. Current values are provisional until chart and operative verification. A row may fail core eligibility, outcome eligibility, or source-quality checks independently."
    ])]
    sections.append(section("Demographics and structural columns", rows=mapped_rows([
        (1,"section_raw","Section label only. Source rows 2, 21, 40 and 63 are administrative headings, not eyes. Preserve in import log."),
        (2,"sex; categorical","Trim and standardize Male and Female; documented spelling Femal maps to Female with rule log. Other or unknown requires source review."),
        (3,"age_source_years; years","Parse 30 y, 46y and plain numbers. Timing is not established; do not claim age at surgery without source verification."),
        (4,"laterality; OD or OS","Right maps to OD, Left to OS after trimming. Patient identity cannot be inferred from laterality."),
        (5,"structural_va_header","Empty divider column; no clinical measurement."),
        (14,"structural_refraction_header","Empty divider column; no clinical measurement."),
        (27,"structural_topography_header","Empty divider column; no clinical measurement."),
        (38,"structural_treatment_header","Empty divider. Treatment values are in column 39, not this column."),
        (41,"structural_safety_header","Empty divider. Haze observations are in column 42.")
    ]),headers=heads))
    sections.append(section("Visual acuity columns", [
        "Each mapped field retains raw notation, chart type, testing distance, correction method, parsed fraction or directly documented logMAR, modifiers, date, conversion rule and review status. A populated source field does not establish a valid model label."
    ], rows=mapped_rows([
        (6,"udva_baseline_raw; then logMAR","Uncorrected baseline distance vision; not a substitute for baseline CDVA."),
        (7,"udva_1m_label_raw; then logMAR","Source one-month label; date unverified."),
        (8,"udva_6m_label_raw; then logMAR","Source six-month label; date unverified."),
        (9,"udva_12m_label_raw; then logMAR","Source twelve-month label; date unverified; not the primary CDVA target."),
        (10,"cdva_baseline_raw; then logMAR","9 populated entries; verify refractive correction and preoperative date."),
        (11,"cdva_1m_label_raw; then logMAR","6 populated entries; interim label, not the target."),
        (12,"cdva_6m_label_raw; then logMAR","5 populated entries; do not carry forward into twelve months."),
        (13,"cdva_12m_label_raw; then logMAR","2 populated entries: row 6 is 20/30- and row 76 is 20/25. No dates verify the endpoint window; row 6 modifier requires review.")
    ]),headers=heads))
    sections.append(section("Refraction columns", [
        "All sphere, cylinder and MRSE fields use dioptres. Keep recorded and calculated MRSE separately. Derive MRSE only from valid paired sphere and cylinder at the same encounter. A trailing plus sign in refraction is a positive sign when the numeric context is clear; the same symbol in visual acuity is a letter modifier."
    ],rows=mapped_rows([
        (15,"sphere_baseline_D","Signed sphere. PL or Pl in this field means plano subject to documented convention, not perception of light."),
        (16,"cylinder_baseline_D","Signed cylinder; confirm cylinder convention."),
        (17,"mrse_baseline_reported_D","Compare with sphere plus half cylinder. Missing reported MRSE may coexist with a valid derived value."),
        (18,"sphere_1m_label_D","Signed sphere at source one-month label."),
        (19,"cylinder_1m_label_D","Signed cylinder at source one-month label."),
        (20,"mrse_1m_label_reported_D","Recorded MRSE; consistency check only."),
        (21,"sphere_6m_label_D","Signed sphere at source six-month label."),
        (22,"cylinder_6m_label_D","Signed cylinder at source six-month label."),
        (23,"mrse_6m_label_reported_D","Recorded MRSE; consistency check only."),
        (24,"sphere_12m_label_D","Signed sphere at source twelve-month label; date unverified."),
        (25,"cylinder_12m_label_D","Signed cylinder at source twelve-month label; date unverified."),
        (26,"mrse_12m_label_reported_D","Recorded MRSE; requires same-visit verification for endpoint analysis.")
    ]),headers=heads))
    sections.append(section("Topography and pachymetry columns",rows=mapped_rows([
        (28,"k1_baseline_D","K1 in dioptres; remove explicit D suffix only after retaining raw."),
        (29,"k2_baseline_D","K2 in dioptres; inspect consistency with K1."),
        (30,"kmax_baseline_D","78 populated entries; candidate predictor after dated scan verification."),
        (31,"thinnest_baseline_source_um","78 entries. Despite loca label, values suggest thickness; confirm TCT meaning and micrometre units before renaming to tct_baseline_um."),
        (32,"pad_d_baseline_source","9 entries. PAD-d may refer to BAD-D; confirm source semantics before mapping to bad_d. No primary model use."),
        (33,"k1_postop_unassigned_D","78 entries. No interval in header; date and visit must be recovered."),
        (34,"k2_postop_unassigned_D","78 entries. Do not assign to twelve months automatically."),
        (35,"kmax_postop_unassigned_D","78 entries. Do not assign to twelve months automatically."),
        (36,"thinnest_postop_unassigned_um","78 entries. Confirm thickness metric, units and date."),
        (37,"pad_d_postop_unassigned_source","7 entries. Confirm score identity, timing and date.")
    ]),headers=heads))
    sections.append(section("Treatment severity and safety columns",rows=mapped_rows([
        (39,"treatment_source_label","44 CXL only, 7 CXL, 27 PRK with CXL and 1 CXL with PTK. Provisional CXL labels do not prove accelerated protocol; PRK label does not prove topography guidance."),
        (40,"amsler_krumeich_stage_source","61 populated entries; stages 1 to 4 allowed after source verification. Do not derive severity solely from Kmax."),
        (42,"haze_postop_source_text","78 entries. No or No haze is explicit absence at an unspecified observation; positive descriptions imply haze, but onset, grade, persistence and endpoint timing remain unverified. Mild old haze requires source adjudication.")
    ]),headers=heads))
    sections.append(section("Required fields absent from the CSV",rows=[
        ["patient_id and eye_id","Text; stable coded keys","Authorized linkage file and eye laterality; essential for grouping bilateral eyes"],
        ["index_date and treatment_verified","ISO date and categorical","Operative and laser records; essential for cohort and follow-up selection"],
        ["visit_id and visit_date","Text and ISO date","Dated clinical encounter; essential for 10 to 14 month endpoint"],
        ["age_index_years","Completed years","Locally calculated from birth date and index date; do not reconstruct from today's age"],
        ["progression_verified and eligibility_reasons","Yes / No / UNK; text","Clinical lead and dated assessments; no inference from one scan"],
        ["cdva_method and chart_type","Categorical and text","Vision/refraction record; spectacle correction and pinhole distinguished"],
        ["scan_date device quality and image_id","Date and coded text","Pentacam or imaging export; optional images and required timing for measured predictors"],
        ["haze_onset resolution and grading scale","Dates and defined grade","Clinical notes; current text cannot establish duration"],
        ["subsequent_treatment and ocular_events","Dated event records","Needed to interpret endpoint treatment pathway"],
        ["source_ref extraction_date and reviewer","Coded references and date","Traceability and adjudication log"]
    ],headers=["Clean fields", "Type and unit", "Source to obtain"]))
    sections.append(section("Header only workbook reconciliation", [
        "The supplied 25240-R Database.xlsx contains a 101-column data-sheet header and no populated patient rows; Codebook contains 82 nonempty rows. It is a proposed collection schema, not additional observations. Its mrn field must become a coded patient ID before analytic export.",
        "The workbook preop_tct field is a candidate source for verified baseline TCT. Keep CCT, apical thickness and TCT distinct. The workbook post-op_cdva diopters header has a unit error: CDVA uses visual-acuity notation or logMAR, never dioptres. Date_of_sx D/M/Y must be parsed with the verified day-month-year convention. The Codebook's preop_cdva and postop_cdva names differ from the displayed headers and require an explicit crosswalk.",
        "Extended topographic indices, aberrometry, densitometry, vectors and haze-resolution fields are optional secondary collections. Their presence in a template does not make them available, validated or part of the primary predictor set."
    ]))
    sections.append(section("Provenance and extraction standards", [
        "Retain a source hash, source row, exact field, raw value, clean value, rule version, timestamp and reviewer for every mapped observation. Prefer a dated operative report for procedure verification and a dated vision/refraction record for CDVA. A disagreement among sources requires clinical adjudication; no global rule can make one note authoritative for every field.",
        "Automated note extraction must record the quoted evidence location, laterality, date, negation and uncertainty. A mention of haze, progression or surgery without a positive finding and relevant chronology does not establish its presence."
    ]))
    return {"number": 3, "title": "KeraNova Data Variable Mapping Sheet", "subtitle": VERSION, "sections": sections}


def cleaning_document() -> dict:
    """Return reproducible raw-data preservation and cleaning specification for document 4."""
    sections = [section("Purpose and current audit", [
        "Apply these rules to a derivative dataset while preserving the original CSV, workbook and authorized source exports. Cleaning resolves formatting and records uncertainty. It does not create missing clinical observations, verify an undocumented procedure, or turn a source-labelled visit into a dated endpoint.",
        "The current CSV audit found 79 eye records after removing four administrative headings from analysis, two ages below 18, no exact duplicate full rows, and two MRSE consistency review candidates. It contains only nine baseline and two source-labelled twelve-month CDVA entries. Patient codes and dates are absent, so the primary model dataset cannot yet be released."
    ])]
    sections.append(section("Storage and change log", [
        "For each clinical variable retain <field>_raw, <field>_clean, <field>_flag and <field>_code. Numeric clean fields contain numeric values or null; missing codes live in the separate code field. The flag field records all applicable rule IDs and review status. Preserve the distinction between a documented value and a calculated derivative.",
        "The change log contains source hash and row, record_id, coded patient_id when recovered, eye_id, variable, rule ID and version, old and new value, reason, extractor or script version, timestamp, reviewer and resolution. Raw files are read only. Save cohort, dictionary, clean data and code versions with each release."
    ]))
    sections.append(section("Missing and negative value codes", rows=[
        ["OBS","Observed usable value","0 and No remain valid observed values"],
        ["ND","Not documented or blank placeholder","Blank, a standalone hyphen, dot, NA-like source placeholder; retain original phrase"],
        ["NA","Not applicable","Only when nonapplicability is explicit; source n/a without context requires review"],
        ["UNK","Explicitly unknown","A source states unknown; distinct from absent information"],
        ["NR","Source not retrievable","Requested record unavailable; state retrieval attempt"],
        ["AMBIG","Unresolved meaning or source conflict","Qualified VA or unidentified metric; do not guess"],
        ["INVALID","Confirmed unusable measurement","Clinical reviewer confirms erroneous or quality-failed value; raw retained"]
    ],headers=["Code", "Meaning", "Rule"]))
    sections.append(section("Import identity and dates", rows=[
        ["R01","Import","Use UTF-8 with BOM tolerance. Validate 42 unique exact CSV headers and consistent row widths. Preserve original punctuation, whitespace and source hash."],
        ["R02","Administrative rows","Exclude source rows 2, 21, 40 and 63 from eye counts only because they have an administrative label and no clinical values. Keep an import disposition log."],
        ["R03","Identifiers","Assign source row IDs such as CSV_R0006. They are record IDs, not patient IDs. Recover patient linkage from the authorized custodian; do not infer identity from age, sex or similar scans."],
        ["R04","Laterality and text","Trim outer spaces in clean text and normalize Right to OD and Left to OS. Femal to Female is a documented spelling correction. Log every changed value; preserve unknown categories."],
        ["R05","Age","Remove y or years suffix and parse a nonnegative age. CSV age timing is unknown. Verify age at treatment and flag values below 18 for the adult-cohort eligibility decision."],
        ["R06","Dates","Normalize verified dates to YYYY-MM-DD with source calendar and day-month-year convention recorded. Resolve ambiguity using source evidence; never infer exact dates from 1, 6 or 12 month labels."],
        ["R07","Chronology","Index date must fall within approved treatment dates; baseline precedes index, or same-day timing proves preoperative status; follow-up is after index. Flag invalid sequences and values after the authorized cutoff."],
        ["R08","Duplicates","Flag exact repeated rows and repeated patient-eye-index keys when IDs are available. Compare source encounter IDs and timestamps; adjudicate conflicting duplicates. Similar age and sex are insufficient to remove a record."]
    ],headers=["Rule", "Area", "Action"]))
    sections.append(section("Numeric measurements and clinical context", rows=[
        ["R09","Numeric parsing","Accept a dot or a verified decimal comma; distinguish decimal from thousands separators. Strip D or micrometre suffix only in the relevant field. Preserve signed values, zero and original precision."],
        ["R10","Refraction signs","A trailing plus such as 0.25+ becomes +0.25 only in a numeric refraction field. PL or Pl in a sphere field is plano under the verified source convention and may become 0 D; it is not light perception."],
        ["R11","MRSE","Calculate sphere plus cylinder divided by 2 from same-encounter valid values. Keep reported MRSE separately; difference greater than 0.02 D flags review. Do not overwrite a reported discrepancy automatically."],
        ["R12","Visual acuity role","Keep UDVA, CDVA, pinhole and contact-lens acuity distinct. Confirm correction and chart method. Do not replace missing CDVA with a different acuity category or postoperative value."],
        ["R13","Visual acuity conversion","For a verified unqualified Snellen fraction n/d, logMAR = log10(d/n); for decimal acuity v > 0, logMAR = -log10(v); retain directly documented logMAR after checking its scale. Record conversion method."],
        ["R14","Modifiers and low vision","Preserve + or - letter modifiers. Do not assume a per-letter correction without chart/scoring evidence. Unresolved qualified values stay AMBIG for primary analysis. CF, HM, LP and NLP remain categorical; no arbitrary numerical primary label."],
        ["R15","Unusual fractions","Fractions such as 4/200 and 25/25-1, and a line labelled 20/24, require chart-distance or transcription verification. Never silently rewrite numerator or denominator to a familiar line."],
        ["R16","Topography timing","Postop K1, K2, Kmax, thinnest and PAD-d lack a time interval. Preserve as unassigned postoperative values until dates and encounters are recovered. Do not use them as baseline predictors."],
        ["R17","Metric identity","Confirm that thinnest loca denotes TCT in micrometres and that PAD-d denotes BAD-D before the respective mappings. Keep central, apical and thinnest thickness separate."],
        ["R18","Scan quality","Use documented scan-quality indicators, laterality, device and scan date. Confirm inconsistent K1/K2 ordering or extreme Kmax against the original scan; retain valid severe-disease measurements."],
        ["R19","Treatment","Normalize source labels provisionally. Verify topography guidance and accelerated CXL before final cohort assignment. The PTK record is a different procedure; retain it in screened records with exclusion reason."],
        ["R20","Haze and safety","No and No haze are explicit negatives for the recorded observation. Positive haze phrases are recorded as positive text with date and grade unverified. Do not infer resolution or standard grade from Mild, +1 or ++ without a documented scale; adjudicate old haze."],
        ["R21","Severity","Accept a documented Amsler Krumeich stage 1 to 4 after verification. Do not reconstruct stage or a mild/severe group from one isolated measurement."]
    ],headers=["Rule", "Area", "Action"]))
    sections.append(section("Range review thresholds", [
        "The following are conservative data-review triggers, not clinical exclusion criteria. A value outside a trigger range remains in the raw data and requires source review; a clinically verified extreme may remain in the clean dataset. Eligibility thickness limits come from the approved clinical protocol, not this table."
    ], rows=[
        ["Age","Less than 0 or greater than 100 years","Under 18 separately triggers adult eligibility review"],
        ["Sphere or cylinder","Absolute value greater than 20 D","Check sign, unit, transcription and cylinder convention"],
        ["K1 K2 or Kmax","Less than 20 D or greater than 100 D","Check device and severe disease; Kmax 96.8 D is not an automatic deletion"],
        ["Corneal thickness","Less than 100 or greater than 1000 micrometres","Check units and whether value is thickness or location"],
        ["logMAR","Less than -0.5 or greater than 2.0","Check chart range and correction; do not cap values"],
        ["Amsler Krumeich stage","Outside 1 to 4","Review documented scale and source"]
    ],headers=["Field", "Review trigger", "Decision"]))
    sections.append(section("Specific findings requiring source review", rows=[
        ["CSV row 23 baseline MRSE","Sphere +1.00 D and cylinder -5.00 D yield -1.50 D; reported +1.50 D","Check source for sign error; retain both until adjudicated"],
        ["CSV row 57 one-month MRSE","Calculated -4.625 D; reported -4.652 D","Difference 0.027 D exceeds 0.02 D trigger; check rounding or transcription"],
        ["CSV row 6 twelve-month CDVA","20/30-","Resolve modifier, correction and actual visit date"],
        ["CSV row 76 twelve-month CDVA","20/25","Verify actual date, correction method and patient linkage"],
        ["CSV rows 20 and 72 ages","17 y and 16y","Verify index age; exclude adult-cohort analysis if confirmed under 18"],
        ["Similar records such as rows 28 and 49","Matching age, sex and several scans with differing refraction and thickness","Possible duplicate candidate only; no deletion without source identity"]
    ],headers=["Record or issue", "Evidence", "Required action"]))
    sections.append(section("Manual review and release criteria", [
        "A second reviewer verifies all final treatment assignments, core eligibility criteria and primary outcome labels. Resolve issues using dated records, document the decision and retain a reason when a value becomes missing or a record is excluded. If a source cannot resolve a conflict, retain AMBIG or NR and report the limitation.",
        "Before release, reconcile 83 imported non-header CSV rows to 79 eye records plus four administrative rows, inspect missingness by treatment and interval, verify patient grouping, dates, endpoint selection and identifiers, and check a sample of every transformation rule independently. No global outcome imputation or carry-forward is allowed. Any predictor imputation or scaling for a future model is learned only from its training data within each resample."
    ]))
    sections.append(section("Measurement reference", [
        "Kaiser PK. Prospective evaluation of visual acuity assessment. Transactions of the American Ophthalmological Society. 2009;107:311–324. https://pmc.ncbi.nlm.nih.gov/articles/PMC2814576/ . The study supports the reciprocal Snellen logMAR conversion and shows that mathematical conversion does not remove chart-method differences. The conservative handling of unresolved modifiers here is a prespecified KeraNova data-quality rule."
    ]))
    return {"number": 4, "title": "KeraNova Data Cleaning Rules", "subtitle": VERSION, "sections": sections}


def transformation_document() -> dict:
    """Return endpoint, derivation, cohort and modeling transformation rules for document 5."""
    sections = [section("Purpose and analytic structure", [
        "This template transforms verified keratoconus observations into a retrospective cohort table and a model table for twelve-month CDVA prediction. It defines calendar-based endpoint selection, clinical derivations, cohort dispositions and patient-level preparation for internal validation.",
        "Keep three linked levels: coded patient, index eye treatment episode, and dated visit or scan. One patient may contribute both eyes; every visit and image for that patient must remain in the same training or validation partition. A stable source record ID does not substitute for patient linkage."
    ])]
    sections.append(section("Interval selection rules",rows=[
        ["Baseline","Nearest valid documented preoperative value for each predictor","Preserve measurement date and lookback. Same-day requires preoperative chronology. Clinically review distant values; interval-restriction sensitivity must be prespecified."],
        ["Interim one month","Actual dated visits or original one-month source label","Descriptive only. No date-based window is inferred from CSV headers; retain actual elapsed time when retrieved."],
        ["Interim six months","Actual dated visits or original six-month source label","Descriptive only; not a substitute for missing twelve-month CDVA."],
        ["Primary twelve-month endpoint","Index date plus 10 calendar months through plus 14 calendar months, inclusive","Select valid CDVA closest in days to the 12-calendar-month anniversary. Equal distance selects earlier visit."],
        ["Other postoperative scan or safety event","Actual dated encounter","Keep separate until timing is verified. Current postop topography and haze fields have unassigned timing."]
    ],headers=["Time point", "Accepted observation", "Selection rule"]))
    sections.append(section("Endpoint algorithm", bullets=[
        "Calculate the 10-, 12- and 14-calendar-month anniversaries from the verified index date. If the starting day does not exist in a target month, use that month's last day. Keep these anniversary dates in the selection log.",
        "Restrict candidate outcomes to the index eye, verified CDVA measurement, usable notation, and visits within the inclusive window. Preserve every candidate and exclusion reason.",
        "Select the candidate with the smallest absolute day distance from the 12-month anniversary. Break a tie by earlier visit date. Resolve differing measurements on the same date using documented correction and method with reviewer adjudication; never choose the better numerical result.",
        "Convert the selected measurement under the frozen visual-acuity rule and record source visit ID, actual date, raw notation, method, logMAR and selection reason. If no valid measurement remains, assign a missing target and keep the eye in the clinical cohort with a stated missing-outcome reason.",
        "Do not interpolate or carry forward labels from 1 or 6 months, UDVA, refraction, pinhole vision, another eye or a public dataset. Do not change the endpoint because of observed model performance."
    ]))
    sections.append(section("Derived variables and direction",rows=[
        ["cdva_12m_logmar","Verified selected endpoint; log10(d/n) for unqualified Snellen n/d","Lower values indicate better vision"],
        ["cdva_baseline_logmar","Verified preoperative corrected vision with conversion rule","Primary baseline predictor"],
        ["delta_cdva_logmar","cdva_12m_logmar minus cdva_baseline_logmar","Negative change indicates improvement"],
        ["mrse_calculated_D","sphere_D plus cylinder_D divided by 2","Same eye and encounter; preserve reported value separately"],
        ["delta_mrse_D","Selected endpoint MRSE minus baseline MRSE","Signed refractive change; not a prediction target"],
        ["delta_kmax_D","Verified same endpoint visit Kmax minus baseline Kmax","Negative change indicates flattening; currently unavailable as timed endpoint"],
        ["delta_tct_um","Verified same endpoint visit TCT minus baseline TCT","Record units and scan quality; thinning alone is not a declared failure"],
        ["elapsed_days","Visit date minus index date","Calendar dates determine endpoint membership"],
        ["elapsed_months_display","elapsed_days divided by 30.4375","Descriptive display only; do not use to replace calendar-month window"],
        ["haze_present_observed","Documented positive or negative observation with date","Primary CSV haze timing is unverified; no resolution-time derivation"],
        ["treatment_group","Verified TG-PRK plus accelerated CXL or accelerated CXL alone","Categorical input; associations do not establish treatment benefit"]
    ],headers=["Variable", "Derivation", "Interpretation"]))
    sections.append(section("Cohort dispositions and denominators", [
        "Assign core eligibility independently from analysis availability. The screened ledger retains all eye records, all criteria, pending verification and exclusions. Use mutually exclusive primary disposition reasons for the flow diagram and retain all secondary reasons for audit. Report patient counts only after coded linkage is recovered.",
        "The clinical descriptive cohort consists of verified adult eligible eyes receiving a qualifying treatment in the approved period. The outcome cohort contains those with a valid primary-window CDVA. The change-from-baseline subset additionally requires valid baseline CDVA. The prediction cohort requires verified patient ID and outcome plus the predictor data permitted by the frozen missingness plan. Report every denominator separately.",
        "The proposal's 30 eyes per group is a planned maximum or target, not an observed result. The present source contains 27 PRK-with-CXL labels, 51 CXL labels and one PTK-with-CXL label before eligibility checks. Do not manufacture records, oversample to create apparent clinical observations, or select patients based on outcome values. Any restriction to a fixed sample must be prespecified with the investigator and independent of outcomes."
    ]))
    sections.append(section("Observed source availability", [
        "Counts below are populated source values after excluding administrative rows; they are not counts of verified calendar-window outcomes. A hyphen or blank is missing. Qualified acuities remain populated for this audit but may be unusable for the primary numeric endpoint until reviewed."
    ],rows=[
        ["Baseline","78","9","Not established"],
        ["One-month source label","65","6","Not established"],
        ["Six-month source label","62","5","Not established"],
        ["Twelve-month source label","39","2","Not established"]
    ],headers=["Source interval", "UDVA populated n", "CDVA populated n", "Verified dated endpoint n"]))
    sections.append(section("Current primary model readiness", [
        "Only CSV rows 6 and 76 contain both baseline and source-labelled twelve-month CDVA. Row 6 contains the unresolved endpoint 20/30-. Row 76 contains 20/25. Both are CXL-labelled records. Their patient linkage, correction methods, treatment protocol and visit dates are unverified. The current export provides no verified primary outcome labels and cannot estimate or validate the proposed multivariable model.",
        "The next authorized extraction must prioritize coded patient and eye identifiers, index and visit dates, true corrected vision at baseline and within 10 to 14 months, verified treatment subtype, baseline Kmax, verified TCT and scan quality. Track recovered, unusable and missing outcomes by treatment group. Public diagnostic imaging data can support a separately labelled exploratory image demonstration, but cannot repair these missing longitudinal outcomes."
    ]))
    sections.append(section("Model input and validation preparation", [
        "Freeze the candidate set to baseline CDVA, age at index treatment, sex, verified treatment group, baseline Kmax and one pachymetry metric. KeraNova prespecifies verified baseline TCT; the current thinnest loca column requires metric confirmation. Do not silently substitute CCT or apical thickness. No postoperative measurement, haze observation or follow-up availability indicator is a baseline predictor.",
        "The primary model uses complete cases for all six prespecified predictors. An optional sensitivity analysis may impute missing baseline Kmax and TCT using training-partition medians and add two missingness indicators. Age, sex, baseline CDVA, verified treatment and patient identifiers must be observed and verified. No alternative predictor-imputation approach is added after examining validation results.",
        "Create patient-level resampling assignments before fitted preprocessing. All data from the same patient, including fellow-eye measurements and images, stay together. Within each training partition only, learn permitted numeric imputation, categorical encoding and scaling; apply that fitted transformation to its held-out patients. Do not fit imputers or transformations once on the entire dataset.",
        "Never impute the primary outcome. Keep raw clinical data without model imputation, and save fold-specific preprocessing parameters separately. If unknown patient IDs or insufficient verified labels prevent grouped validation, do not report internal-validation performance."
    ]))
    sections.append(section("Safety events and optional secondary outcomes", [
        "Preserve dated complications and subsequent procedures through the endpoint. Do not automatically discard postoperative values after a complication; report the treatment pathway and apply the prespecified secondary sensitivity analysis when the data supports it. Haze resolution requires documented onset, dated positive and negative observations and a defined grading scale. The current CSV supports neither time-to-resolution estimates nor a validated postoperative haze grade.",
        "Any definition of clinical progression, stability, two-line change or safety loss requires agreement on the actual chart and measurement method before analysis. LogMAR change can be reported numerically without claiming an unsupported line-equivalent threshold."
    ]))
    sections.append(section("Verification and release checklist", bullets=[
        "Reconcile administrative rows, screened eye records, unique patients, final eligibility, exclusions, pending records, available labels and each analysis denominator.",
        "Recompute representative Snellen conversions and MRSE independently. Check date-window boundaries, calendar end-of-month behavior and equal-distance tie selection with the actual chosen endpoint log.",
        "Verify all target and treatment assignments against records. Check that postoperative information is absent from the predictor matrix and that no patient overlaps training and validation partitions.",
        "Freeze source hash, dictionary version, cohort ledger, clean dataset, analysis specification and transformation log. Data release approvals and signatures: clinical lead __________ data custodian __________ statistician __________ date __________."
    ]))
    return {"number": 5, "title": "KeraNova Data Transformation Template", "subtitle": VERSION, "sections": sections}


if __name__ == "__main__":
    documents = [collection_document(), mapping_document(), cleaning_document(), transformation_document()]
    output = BUILD / "data_workflow.json"
    output.write_text(json.dumps({str(document["number"]): document for document in documents}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(output))
    print([(document["number"], len(document["sections"])) for document in documents])
