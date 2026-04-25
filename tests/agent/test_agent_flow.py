import pytest

from src.services.data_extraction_service import (
    normalize_raw_record,
    validate_extracted_record,
)


@pytest.mark.integration
@pytest.mark.critical
def test_agent_extraction_schema_valid_record():
    """
    Clinical safety check: extraction agent preserves required fields and types.
    """
    raw_record = {
        "patient_id": "PT-1001",
        "age": 54,
        "symptoms": ["chest pain", "fatigue"],
        "source": " PATIENT_PORTAL ",
    }

    extracted = normalize_raw_record(raw_record)
    errors = validate_extracted_record(extracted)

    assert errors == []
    assert extracted.source_system == "patient_portal"


@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.parametrize(
    "raw_record,expected_error",
    [
        (
            {"patient_id": "PT-2001", "age": "54", "symptoms": ["cough"], "source": "fax_line"},
            "invalid type for age",
        ),
        (
            {"patient_id": "PT-2002", "age": 155, "symptoms": ["fever"], "source": "claims_system"},
            "age out of acceptable range",
        ),
        (
            {"patient_id": "PT-2003", "age": 40, "symptoms": ["fever", 123], "source": "patient_portal"},
            "symptoms must be list[str]",
        ),
        (
            {"patient_id": "2003", "age": 40, "symptoms": ["fever"], "source": "patient_portal"},
            "patient_id format must match PT-<digits>",
        ),
        (
            {"patient_id": "PT-2004", "age": 40, "symptoms": ["fever"], "source": "email_csv"},
            "source_system must be one of",
        ),
    ],
)
def test_agent_extraction_schema_rejects_unsafe_payloads(raw_record, expected_error):
    """
    Clinical safety check: malformed extracted payloads are detected early.
    """
    extracted = normalize_raw_record(raw_record)
    errors = validate_extracted_record(extracted)
    assert any(expected_error in error for error in errors)