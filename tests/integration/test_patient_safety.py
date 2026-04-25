import pytest
from src.services.model_service import predict


@pytest.mark.critical
def test_no_blank_symptoms():

    data = {
        "age": 50,
        "symptoms": "",
        "history": "diabetes"
    }

    result = predict(data)

    # Ensure model does not misclassify silently
    assert result["risk_level"] != "high"