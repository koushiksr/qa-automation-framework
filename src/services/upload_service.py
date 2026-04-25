"""
Medical chart upload validation service.

Encapsulates the real-world business rules for what uploads the platform accepts.
Tests assert behavior of this module instead of embedding simulated logic.
"""

from typing import Dict, Any


ALLOWED_FORMATS = {"pdf", "tiff", "png"}
MAX_PAGES = 50
MAX_FILE_SIZE_MB = 20


def validate_chart_upload(file_ext: str, pages: int, size_mb: int) -> Dict[str, Any]:
    """
    Validate a medical chart upload request.

    Returns a response dict with:
        - accepted: bool
        - error_code: Optional[str]
        - message: str
    """
    ext = (file_ext or "").lower()

    if ext not in ALLOWED_FORMATS:
        return {
            "accepted": False,
            "error_code": "INVALID_FORMAT",
            "message": "Unsupported file format. Please upload PDF, TIFF, or PNG.",
        }

    if pages > MAX_PAGES:
        return {
            "accepted": False,
            "error_code": "PAGE_LIMIT_EXCEEDED",
            "message": f"Chart exceeds maximum page limit ({MAX_PAGES}).",
        }

    if size_mb > MAX_FILE_SIZE_MB:
        return {
            "accepted": False,
            "error_code": "FILE_SIZE_EXCEEDED",
            "message": f"File size exceeds {MAX_FILE_SIZE_MB}MB limit.",
        }

    return {"accepted": True, "error_code": None, "message": "Upload successful."}

