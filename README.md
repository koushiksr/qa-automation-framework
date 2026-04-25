# Pytest Automation Framework

A modular, clean, and feature-rich pytest framework with category-based execution, enhanced logging, HTML dashboard, and CI/CD integration.

## Features

- **Modular Architecture**: Clean separation of concerns with base classes for different test types
- **Category-Based Execution**: Run tests by markers (smoke, regression, critical, api, ui, etc.)
- **Enhanced Logging**: Console + file logging with loguru, test-specific context
- **Execution Time Tracking**: Per-test timing with history and trend analysis
- **Pass/Fail History**: JSON-based history tracking across runs
- **HTML Dashboard**: Interactive reports with charts, trends, and category breakdowns
- **CI/CD Ready**: Jenkinsfile with parallel execution and quality gates
- **Allure Integration**: Full Allure reporting support

## Project Structure

```
qa_automation_framework/
├── src/
│   ├── config/
│   │   ├── config.yaml          # Framework configuration
│   │   └── settings.py          # Settings manager
│   ├── core/
│   │   ├── base_test.py         # Base test classes (BaseTest, APITest, UITest)
│   │   ├── logger.py            # Enhanced logging system
│   │   └── constants.py         # Shared constants
│   ├── utils/
│   │   ├── assertions.py        # Enhanced assertion helpers
│   │   ├── helpers.py           # Utility functions
│   │   └── test_history.py      # History tracking
│   └── reporting/
│       └── dashboard.py         # HTML dashboard generator
├── tests/
│   ├── conftest.py              # Pytest hooks and fixtures
│   └── example/                 # Example tests
│       ├── test_api_examples.py
│       ├── test_ui_examples.py
│       └── test_integration_examples.py
├── reports/
│   ├── html/                    # HTML reports
│   ├── allure-results/          # Allure raw data
│   ├── allure-report/           # Allure generated report
│   ├── history/                 # Test history JSON
│   └── logs/                    # Log files
├── scripts/
│   ├── run_tests.bat            # Test runner script
│   ├── view_report.bat          # Open reports
│   └── show_history.bat         # View history
├── Jenkinsfile                  # CI/CD pipeline
├── pytest.ini                   # Pytest configuration
└── requirements.txt             # Python dependencies
```

## Quick Start

### Run All Tests
```bash
scripts\run_tests.bat
```

### Run by Category
```bash
scripts\run_tests.bat smoke
scripts\run_tests.bat api
scripts\run_tests.bat regression parallel
scripts\run_tests.bat critical verbose
```

### Run Specific Test File
```bash
scripts\run_tests.bat tests\example\test_api_examples.py
```

### View Reports
```bash
scripts\view_report.bat          # Open all reports
scripts\view_report.bat allure   # Open Allure report
scripts\view_report.bat html     # Open HTML dashboard
```

## Markers/Categories

| Marker | Description | Use Case |
|--------|-------------|----------|
| `smoke` | Quick validation tests | Pre-merge checks |
| `regression` | Full suite regression | Nightly builds |
| `critical` | High-risk tests | Release gates |
| `api` | API/backend tests | Backend validation |
| `ui` | UI tests | Frontend validation |
| `integration` | Integration tests | Component interaction |
| `performance` | Performance tests | Load/stress testing |
| `slow` | Long-running tests | Exclude from quick runs |
| `wip` | Work in progress | Expected to fail |
| `flaky` | Known flaky tests | Use with --reruns |

## Writing Tests

### Basic Test
```python
from src.core.base_test import BaseTest

class TestMyFeature(BaseTest):

    @pytest.mark.smoke
    def test_something(self):
        self.log_info("Starting test")
        # Test logic here
        self.log_success("Test passed")
```

### API Test
```python
from src.core.base_test import APITest

class TestAPI(BaseTest):

    @pytest.mark.api
    @pytest.mark.regression
    def test_api_endpoint(self):
        self.log_info("Testing API endpoint")
        response = requests.get(f"{base_url}/endpoint")
        assert response.status_code == 200
```

### Using Assertions
```python
from src.utils.assertions import assert_equal, assert_in, assert_true

def test_with_assertions(self):
    result = get_result()
    assert_equal(result.status, "success")
    assert_in("expected_value", result.data)
    assert_true(result.is_valid)
```

## Configuration

### pytest.ini
Edit `pytest.ini` to customize:
- Test paths
- Markers
- Logging levels
- Timeout settings

### config.yaml
Edit `src/config/config.yaml` for:
- Environment settings (base_url, timeouts)
- Logging configuration
- Report settings
- Category-specific timeouts

## HTML Dashboard

The dashboard includes:
- **Summary Cards**: Total, Passed, Failed, Pass Rate, Duration
- **Trend Charts**: Pass rate and duration over time
- **Category Statistics**: Breakdown by marker
- **Flaky Tests**: Tests with inconsistent results
- **Run History**: Historical test runs
- **Detailed Results**: Per-test status, duration, errors

## CI/CD Pipeline

The Jenkinsfile provides:
- **Parameterized Builds**: Choose test suite, parallel execution
- **Parallel Execution**: Run test categories in parallel
- **Quality Gates**: Fail build if pass rate below threshold
- **Allure Publishing**: Automatic Allure report generation
- **Artifact Archiving**: Store reports for later access

### Jenkins Parameters
- `TEST_SUITE`: all, smoke, regression, critical, api, ui, integration
- `PARALLEL_EXEC`: Run tests in parallel
- `GENERATE_DASHBOARD`: Generate HTML dashboard
- `PYTEST_ARGS`: Additional pytest arguments

## History Tracking

Test history is stored in `reports/history/test_history.json`:
- Per-test pass/fail status
- Execution duration
- Timestamp
- Markers/categories
- Error messages

### View History
```bash
scripts\show_history.bat
scripts\show_history.bat smoke    # Category stats
scripts\show_history.bat test_name  # Test-specific stats
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `pytest -m smoke` | Run smoke tests |
| `pytest -m "api and not slow"` | Run API tests excluding slow |
| `pytest -n auto` | Run tests in parallel |
| `pytest --reruns 2` | Rerun failed tests 2 times |
| `pytest --html=report.html` | Generate HTML report |
| `pytest -vv` | Extra verbose output |

## Dependencies

Install dependencies:
```bash
pip install -r requirements.txt
```

Key packages:
- pytest: Test runner
- pytest-html: HTML reports
- allure-pytest: Allure integration
- pytest-xdist: Parallel execution
- pytest-rerunfailures: Rerun failed tests
- loguru: Enhanced logging
