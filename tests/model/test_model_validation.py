import pytest
from src.clients.model_client import predict_risk

@pytest.mark.api
@pytest.mark.critical
def test_valid_patient():
    data = {"age": 65}
    res = predict_risk(data)
    assert res["risk"] == "high"


@pytest.mark.api
def test_invalid_age_type():
    data = {"age": "sixty"}
    res = predict_risk(data)
    assert "validation error" in res["error"]