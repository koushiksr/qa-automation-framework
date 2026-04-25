import pytest
from src.services.model_service import predict
from src.utils.data_loader import load_test_data

test_data = load_test_data("data/patient_data.json")


@pytest.mark.regression
@pytest.mark.api
@pytest.mark.parametrize("case", test_data)
def test_model_integration(case):

    input_data = case["input"]

    if "expected_error" in case:
        with pytest.raises((ValueError, TypeError)) as e:
            predict(input_data)

        assert case["expected_error"] in str(e.value)

    else:
        result = predict(input_data)

        assert result["risk_level"] == case["expected"]["risk_level"]