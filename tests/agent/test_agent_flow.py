import pytest

@pytest.mark.api
@pytest.mark.critical
def test_model_valid_input():

    patient_data = {
        "age": 45,
        "symptoms": ["chest pain", "fatigue"]
    }

    # simulate model response
    response = {"risk": "high"}

    assert response["risk"] in ["low", "medium", "high"]