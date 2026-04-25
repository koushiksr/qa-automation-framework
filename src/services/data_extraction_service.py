"""
Healthcare data extraction service used by the Agentic platform.

This module represents the real extraction contract that the agent must satisfy.
Tests should validate this behavior end-to-end rather than simulating logic in the test layer.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import re


@dataclass
class ExtractedPatientRecord:
    patient_id: str
    age: int
    symptoms: List[str]
    source_system: str


REQUIRED_EXTRACTION_FIELDS: Dict[str, type] = {
    "patient_id": str,
    "age": int,
    "symptoms": list,
    "source_system": str,
}
ALLOWED_SOURCE_SYSTEMS = {"patient_portal", "fax_line", "claims_system"}
PATIENT_ID_PATTERN = re.compile(r"^PT-\d{4,}$")


def normalize_raw_record(raw_record: Dict[str, Any]) -> ExtractedPatientRecord:
    """
    Normalize a raw payload coming from a portal/fax/claims system into
    the canonical `ExtractedPatientRecord` used by the platform.
    """
    normalized = {
        "patient_id": str(raw_record.get("patient_id", "")).strip(),
        "age": raw_record.get("age"),
        "symptoms": raw_record.get("symptoms", []),
        "source_system": str(raw_record.get("source", "unknown")).strip().lower(),
    }
    return ExtractedPatientRecord(**normalized)


def validate_extracted_record(record: ExtractedPatientRecord) -> List[str]:
    """
    Validate an extracted record against the contract expected by downstream models.

    Returns a list of human-readable validation error messages.
    """
    errors: List[str] = []

    as_dict = {
        "patient_id": record.patient_id,
        "age": record.age,
        "symptoms": record.symptoms,
        "source_system": record.source_system,
    }

    for field, expected_type in REQUIRED_EXTRACTION_FIELDS.items():
        if as_dict.get(field) is None:
            errors.append(f"missing field: {field}")
            continue
        if not isinstance(as_dict[field], expected_type):
            errors.append(
                f"invalid type for {field}: expected {expected_type.__name__}, "
                f"got {type(as_dict[field]).__name__}"
            )

    if isinstance(record.age, int) and (record.age < 0 or record.age > 120):
        errors.append("age out of acceptable range")

    if isinstance(record.symptoms, list) and any(
        not isinstance(item, str) for item in record.symptoms
    ):
        errors.append("symptoms must be list[str]")

    if isinstance(record.patient_id, str) and not PATIENT_ID_PATTERN.match(record.patient_id):
        errors.append("patient_id format must match PT-<digits>")

    if isinstance(record.source_system, str) and record.source_system not in ALLOWED_SOURCE_SYSTEMS:
        errors.append("source_system must be one of patient_portal, fax_line, claims_system")

    return errors

