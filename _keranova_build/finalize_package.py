"""Assemble the committee package and verified public-data provenance.

This script copies the reviewed seven documents to their requested root paths,
leaves raw data unchanged, and creates a ZIP without QA files or original
identifier-bearing public workbooks. It also writes a readable readiness note.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "_keranova_build"
OUTPUT = ROOT / "KeraNova_Submission"


def dataset_memo(research: dict) -> str:
    """Format verified dataset evidence as an accessible text memo.

    Args:
        research: Public-source evidence from the dataset-search agent.
    Returns:
        Text with source links, access, fit and important limitations.
    """
    lines = ["KeraNova Public Dataset Search", "Checked 1 October 2026", "",
             "No exact public replacement for the planned TG-PRK plus accelerated CXL versus accelerated CXL cohort with dated twelve-month CDVA and linked images was verified.", "",
             "Preferred outcome source: Wajnsztajn et al. supporting data. A separate CXL-only nominal-one-year feasibility experiment may be possible after source checks. The downloaded data has 334 baseline/nominal-one-year pairs across 251 source patient IDs before adult, completeness and quality screening.", "",
             "Preferred image source: CornOrb, with 1,454 examinations from 744 patients and four corneal maps per examination. It is a diagnostic dataset without postoperative CDVA. Its 680 MB archive was not downloaded. Repository and paper licence wording differ; clarify before commercial reuse.", ""]
    for item in research["candidates"]:
        lines.extend([f"{item['rank']}. {item['title']}", f"Source: {item['repository_url']}",
                      f"Access: {item['access']}", f"Licence: {item['license']}",
                      f"Suggested use: {item['recommended_use']}"])
        for limitation in item.get("limitations", []):
            lines.append(f"Limitation: {limitation}")
        lines.append("")
    lines.extend(["Files acquired", "Raw publisher XLSX and Mendeley SAV are retained separately in Public_Datasets.",
                  "The committee package contains only the PLOS pseudonymous derivative, source verification evidence and this memo. Source ID and file-number fields are omitted from the derivative.",
                  "No public model has been trained. Public data must remain separate from institutional patient data.", ""])
    return "\n".join(lines)


def readiness_note() -> str:
    """Return the committee status and decisions required before analysis.

    Returns:
        Plain-text readiness statement; does not assert committee approval.
    """
    return """KeraNova Committee Package
Version 1.0 | 1 October 2026

Submission purpose
The seven completed documents specify the retrospective study and exploratory
prediction of twelve-month corrected distance visual acuity (CDVA) in logMAR.
They are a protocol, collection specification and analysis plan, not completed
clinical results or a trained model. Collection entry spaces and dummy-table
shells are intentionally unpopulated. No performance metrics were fabricated.

Completed
1. Methodology aligned with the revised KeraNova proposal.
2. Eye-level collection form, eligibility checklist and dated visit form.
3. Mapping of all 42 exact CSV headers and required missing source fields.
4. Cleaning rules, review triggers, missing codes and correction provenance.
5. Calendar-based endpoint selection, derivations and analysis populations.
6. Prespecified ridge model, benchmark, patient-grouped validation and uncertainty.
7. Clinical, safety and prediction table shells and figure specifications.

Current institutional data status
The unchanged CSV contains 79 eye-like records and four administrative headings.
Treatment labels: 27 PRK with CXL, 51 CXL/CXL-only and one PTK with CXL.
Only nine baseline and two nominal twelve-month corrected-vision fields are
populated. One endpoint is qualified Snellen notation requiring adjudication.
Neither patient linkage nor actual treatment/visit dates is present. No verified
primary-window target can be released from this extract. These counts are not
the achieved eligible study sample. Primary institutional modelling was not run.

Public-data option
The PLOS derivative provides a distinct CXL-only nominal-one-year experiment,
with 334 baseline/one-year pairs across 251 source IDs before further screening.
Its conventional/accelerated CXL mix has no TG-PRK comparator and no actual visit
dates or laterality. Source patient identity anomalies, negative last-follow-up
metadata, adulthood and correction methods require review. Central pachymetry
must not be renamed TCT. This option does not validate the institutional model.
CornOrb offers diagnostic corneal maps, not treatment-outcome targets.

Investigator and biostatistician decisions
- Confirm the primary CDVA target and the six baseline predictor terms.
- Confirm exact treatment-period boundaries and the operative procedure types.
- Reconcile minimum twelve-month follow-up with the ten-to-fourteen-month window.
- Confirm the progressive-keratoconus evidence and procedure-specific eligibility.
- Resolve parent pregnancy/lactation and consent/waiver wording against the
  actual IRB determination; verify AI-extension amendment/formal determination.
- Recover coded patient/eye IDs, dated baseline and follow-up CDVA and true TCT.
- Evaluate independent-patient sample adequacy before the specified validation.
- Confirm the separate public-feasibility protocol before public model fitting.

Verification performed
Independent agents reviewed clinical/statistical consistency and the source data.
All exact CSV columns were mapped; source availability and public endpoints were
recounted. Public one-year logMAR and decimal BCVA reconciled in 336 available
records. The seven saved DOCX packages reopened and passed content checks.
Every final page preview was inspected, with layout corrections applied.
The native Word/LibreOffice renderer was unavailable on this host. A local
Aspose evaluation renderer was used only for internal previews; mapping and
table documents were reviewed as their explicitly paginated chapters. Native
Word pagination was not independently verified. Final DOCX files contain no
Aspose evaluation marks, and no intermediate PDFs/PNGs are included here.

What remains
Clinical/IRB decisions and source-data verification remain required before
institutional analysis. No external committee submission has been sent.
Original glaucoma templates are preserved in Original_Glaucoma_Templates_2026-10-01.
The requested seven root files now contain the completed KeraNova versions.
"""


def verify_source_integrity() -> None:
    """Verify the clinical CSV and original document backups are unchanged.

    Returns:
        None. Raises rather than finalize a package with an integrity failure.
    Raises:
        ValueError: If a raw file or backup hash differs from the saved audit.
    """
    audit = json.loads((BUILD / "data_audit.json").read_text(encoding="utf-8"))
    actual = hashlib.sha256((ROOT / "dataset.csv").read_bytes()).hexdigest()
    if actual != audit["csv"]["sha256"]:
        raise ValueError("Raw clinical CSV changed")
    original = json.loads((BUILD / "original_document_hashes.json").read_text(encoding="utf-8-sig"))
    for item in original:
        path = ROOT / "Original_Glaucoma_Templates_2026-10-01" / item["File"]
        if hashlib.sha256(path.read_bytes()).hexdigest().upper() != item["OriginalSHA256"]:
            raise ValueError(f"Original backup changed: {path.name}")


def main() -> None:
    """Write supporting notes, finalize requested paths, and create the ZIP.

    Returns:
        None. Writes final documents and a shareable committee package.
    Raises:
        ValueError or OSError: If integrity checks or finalization fail.
    """
    verify_source_integrity()
    research = json.loads((BUILD / "public_datasets.json").read_text(encoding="utf-8"))
    (OUTPUT / "Public_Dataset_Search.txt").write_text(dataset_memo(research), encoding="utf-8")
    (OUTPUT / "Committee_Readiness.txt").write_text(readiness_note(), encoding="utf-8")
    public = OUTPUT / "Public_Data"
    public.mkdir(exist_ok=True)
    derivative = ROOT / "Public_Datasets" / "Wajnsztajn_2022_CXL_research_derivative.csv"
    shutil.copy2(derivative, public / derivative.name)
    provenance = json.loads(json.dumps(research))
    provenance.pop("file_verification_artifact", None)
    for candidate in provenance["candidates"]:
        for key in list(candidate):
            if key.startswith("local_"):
                candidate.pop(key)
    (public / "Dataset_Provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    source = research["candidates"][0]
    verification = {"checked_date": research["checked_date"], "source_url": source["repository_url"],
                    "raw_sha256": source["raw_sha256"], "derivative_sha256": source["derivative_sha256"],
                    "outcome_counts": source["outcome_counts_verified_from_file"],
                    "limitations": source["limitations"]}
    (public / "Source_File_Verification.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    for path in OUTPUT.glob("*.docx"):
        shutil.copy2(path, ROOT / path.name)
    archive = ROOT / "KeraNova_Committee_Package_2026-10-01.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(OUTPUT))
    print(f"Created {archive}; {archive.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
