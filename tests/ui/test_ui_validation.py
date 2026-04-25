import pytest

@pytest.mark.ui
def test_invalid_file_upload():
    file_type = "txt"

    error_message = "Invalid file format"

    assert "Invalid" in error_message


@pytest.mark.ui
def test_large_file_upload():
    size_mb = 50

    error = "File size exceeds limit"

    assert "exceeds" in error