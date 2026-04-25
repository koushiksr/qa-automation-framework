import pytest

from src.services.upload_service import validate_chart_upload


@pytest.mark.ui
@pytest.mark.critical
def test_invalid_file_upload_rejected_with_clear_message():
    response = validate_chart_upload(file_ext="txt", pages=3, size_mb=1)
    assert response["accepted"] is False
    assert response["error_code"] == "INVALID_FORMAT"
    assert "Unsupported file format" in response["message"]


@pytest.mark.ui
@pytest.mark.regression
def test_large_file_upload_rejected():
    response = validate_chart_upload(file_ext="pdf", pages=3, size_mb=50)
    assert response["accepted"] is False
    assert response["error_code"] == "FILE_SIZE_EXCEEDED"
    assert "20MB" in response["message"]


@pytest.mark.ui
@pytest.mark.critical
def test_too_many_pages_upload_rejected():
    response = validate_chart_upload(file_ext="pdf", pages=125, size_mb=8)
    assert response["accepted"] is False
    assert response["error_code"] == "PAGE_LIMIT_EXCEEDED"
    assert "maximum page limit" in response["message"]


@pytest.mark.ui
@pytest.mark.smoke
def test_valid_chart_upload_is_accepted():
    response = validate_chart_upload(file_ext="pdf", pages=10, size_mb=5)
    assert response["accepted"] is True
    assert response["error_code"] is None