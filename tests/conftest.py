"""
Pytest conftest.py - Central hook registrations and fixtures.
Handles: test timing, history tracking, HTML report generation, allure labels.
"""
import pytest
import time
from datetime import datetime

from src.utils.test_history import get_history_tracker
from src.reporting.dashboard import DashboardGenerator


# ---------------------------
# GLOBAL STATE
# ---------------------------
test_results = []
test_start_times = {}


# ---------------------------
# PYTEST HOOKS
# ---------------------------

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: quick validation tests")
    config.addinivalue_line("markers", "regression: full suite regression tests")
    config.addinivalue_line("markers", "critical: high-risk patient safety tests")
    config.addinivalue_line("markers", "api: model/backend API tests")
    config.addinivalue_line("markers", "ui: UI validation tests")
    config.addinivalue_line("markers", "integration: integration tests between components")
    config.addinivalue_line("markers", "performance: performance and load tests")
    config.addinivalue_line("markers", "slow: tests that take longer to execute")
    config.addinivalue_line("markers", "wip: work in progress tests")
    config.addinivalue_line("markers", "flaky: known flaky tests")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Apply Allure labels based on markers before test setup."""
    _apply_allure_labels(item)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Record test start time before execution."""
    test_id = item.nodeid
    test_start_times[test_id] = time.time()
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture test results with timing information.
    This hook wraps the test result creation.
    """
    outcome = yield
    report = outcome.get_result()

    # Only process actual test results (not setup/teardown)
    if report.when != "call":
        return

    test_id = item.nodeid
    duration = time.time() - test_start_times.get(test_id, time.time())

    # Determine status
    status = "passed" if report.passed else "failed" if report.failed else "skipped"

    # Get markers/categories
    markers = [m.name for m in item.iter_markers()]

    # Get error message if failed
    error = str(call.excinfo.value) if call.excinfo else None

    # Create result entry
    result_entry = {
        "name": test_id,
        "short_name": item.name,
        "duration": round(duration, 3),
        "status": status,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "markers": markers,
    }

    test_results.append(result_entry)

    # Attach stdout/stderr to Allure if available
    _attach_logs_to_allure(report)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Called after entire test session completes.
    Saves history, generates reports.
    """
    history_tracker = get_history_tracker()

    # Save results to history
    for result in test_results:
        history_tracker.add_result(
            test_name=result['name'],
            status=result['status'],
            duration=result['duration'],
            markers=result['markers'],
            error=result.get('error')
        )

    # Save run to history file
    history_tracker.save_run(exitstatus)

    # Generate HTML dashboard
    generate_dashboard_report(history_tracker, exitstatus)

    # Print summary
    _print_summary(test_results, exitstatus)


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def _apply_allure_labels(item):
    """Apply Allure labels dynamically based on test markers."""
    try:
        import allure
    except ImportError:
        return

    markers = [m.name for m in item.iter_markers()]

    # Map markers to Allure severity
    severity_map = {
        "critical": allure.severity_level.CRITICAL,
        "blocker": allure.severity_level.BLOCKER,
        "high": allure.severity_level.CRITICAL,
        "medium": allure.severity_level.NORMAL,
        "low": allure.severity_level.MINOR,
    }

    for marker in markers:
        if marker in severity_map:
            allure.dynamic.severity(severity_map[marker])

    # Set feature based on category
    if "api" in markers:
        allure.dynamic.feature("API Tests")
        allure.dynamic.suite("API Suite")
    elif "ui" in markers:
        allure.dynamic.feature("UI Tests")
        allure.dynamic.suite("UI Suite")
    elif "integration" in markers:
        allure.dynamic.feature("Integration Tests")
        allure.dynamic.suite("Integration Suite")
    elif "performance" in markers:
        allure.dynamic.feature("Performance Tests")
        allure.dynamic.suite("Performance Suite")
    else:
        allure.dynamic.feature("General Tests")

    # Add all markers as tags
    if markers:
        allure.dynamic.tag(*markers)


def _attach_logs_to_allure(report):
    """Attach stdout/stderr and error info to Allure report."""
    try:
        import allure
    except ImportError:
        return

    # Attach stdout
    if hasattr(report, 'capstdout') and report.capstdout:
        allure.attach(
            report.capstdout,
            name="stdout",
            attachment_type=allure.attachment_type.TEXT
        )

    # Attach stderr
    if hasattr(report, 'capstderr') and report.capstderr:
        allure.attach(
            report.capstderr,
            name="stderr",
            attachment_type=allure.attachment_type.TEXT
        )

    # Attach error trace if failed
    if report.failed and hasattr(report, 'longrepr') and report.longrepr:
        allure.attach(
            str(report.longrepr),
            name="error_trace",
            attachment_type=allure.attachment_type.TEXT
        )


def generate_dashboard_report(history_tracker, exitstatus):
    """Generate HTML dashboard report."""
    try:
        dashboard = DashboardGenerator()

        # Get current run data
        current_run = {
            'summary': history_tracker._calculate_summary(test_results),
            'tests': test_results
        }

        report_path = dashboard.generate(current_run=current_run)
        print(f"\n HTML Dashboard generated: {report_path}")

    except Exception as e:
        print(f" Warning: Dashboard generation failed: {e}")


def _print_summary(results, exitstatus):
    """Print test summary to console."""
    total = len(results)
    passed = len([r for r in results if r['status'] == 'passed'])
    failed = len([r for r in results if r['status'] == 'failed'])
    skipped = len([r for r in results if r['status'] == 'skipped'])
    total_duration = sum(r['duration'] for r in results)

    print("\n" + "=" * 60)
    print(" TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f" Total Tests:    {total}")
    print(f" Passed:         {passed} ")
    print(f" Failed:         {failed} ")
    print(f" Skipped:        {skipped}")
    print(f" Pass Rate:      {(passed/total*100) if total > 0 else 0:.1f}%")
    print(f" Total Duration: {total_duration:.2f}s")
    print(f" Avg Duration:   {(total_duration/total) if total > 0 else 0:.3f}s")
    print("=" * 60)

    # Show failed tests
    if failed > 0:
        print("\n FAILED TESTS:")
        for r in results:
            if r['status'] == 'failed':
                print(f"  - {r['name']} ({r['duration']:.3f}s)")
                if r.get('error'):
                    print(f"    Error: {r['error'][:100]}...")
    print("=" * 60)


# ---------------------------
# SHARED FIXTURES
# ---------------------------

@pytest.fixture
def test_context(request):
    """
    Provides test context with metadata.
    Usage: def test_something(test_context):
    """
    markers = [m.name for m in request.node.iter_markers()]
    return {
        'test_name': request.node.name,
        'test_path': request.node.nodeid,
        'markers': markers,
        'timestamp': datetime.now().isoformat()
    }


@pytest.fixture
def timing(request):
    """
    Provides timing information for the current test.
    Usage: def test_something(timing):
    """
    return {
        'start_time': test_start_times.get(request.node.nodeid),
        'get_elapsed': lambda: time.time() - test_start_times.get(request.node.nodeid, time.time())
    }
