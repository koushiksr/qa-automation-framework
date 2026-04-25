import pytest
from src.core.base_test import BaseTest

@pytest.mark.smoke
@pytest.mark.api
class TestSample(BaseTest):

    def test_example(self):
        assert 1 == 1