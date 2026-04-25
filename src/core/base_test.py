"""
Base test class with setup/teardown, logging, and common utilities.
All test classes should inherit from this.
"""
import pytest
import time
from typing import Any, Optional
from src.core.logger import get_logger
from src.config.settings import settings


class BaseTest:
    """
    Base class for all tests.
    Provides: automatic setup/teardown, logging, timing, and common utilities.
    """

    logger = get_logger()
    start_time: Optional[float] = None
    test_data: dict = {}

    @pytest.fixture(autouse=True)
    def setup_teardown(self, request):
        """
        Automatic setup and teardown for all tests.
        Logs execution time and handles cleanup.
        """
        test_name = request.node.name
        markers = [m.name for m in request.node.iter_markers()]

        self.start_time = time.time()
        self.logger.set_test_context(test_name, category=markers[0] if markers else None)
        self.logger.info("=" * 60)
        self.logger.info(f"STARTING: {test_name}")
        self.logger.info(f"Categories: {', '.join(markers) if markers else 'none'}")
        self.logger.info("=" * 60)

        yield

        elapsed = time.time() - self.start_time
        self.logger.info("=" * 60)
        self.logger.info(f"COMPLETED: {test_name} in {elapsed:.3f}s")
        self.logger.info("=" * 60)
        self.logger.clear_test_context()

    def log_info(self, message: str):
        """Log info message with test context."""
        self.logger.info(message)

    def log_debug(self, message: str):
        """Log debug message with test context."""
        self.logger.debug(message)

    def log_warning(self, message: str):
        """Log warning message with test context."""
        self.logger.warning(message)

    def log_error(self, message: str):
        """Log error message with test context."""
        self.logger.error(message)

    def log_success(self, message: str):
        """Log success message with test context."""
        self.logger.success(message)

    def get_elapsed_time(self) -> float:
        """Get elapsed time since test start."""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0

    def set_test_data(self, key: str, value: Any):
        """Store test data for later use."""
        self.test_data[key] = value

    def get_test_data(self, key: str, default: Any = None) -> Any:
        """Retrieve stored test data."""
        return self.test_data.get(key, default)


class APITest(BaseTest):
    """Base class for API tests with additional API-specific utilities."""

    api_timeout: int = 30

    @pytest.fixture(autouse=True)
    def api_setup(self):
        """API-specific setup."""
        self.api_timeout = settings.environment.get('api_timeout', 30)
        self.log_info(f"API timeout set to {self.api_timeout}s")
        yield


class UITest(BaseTest):
    """Base class for UI tests with browser management."""

    ui_timeout: int = 60

    @pytest.fixture(autouse=True)
    def ui_setup(self):
        """UI-specific setup."""
        self.ui_timeout = settings.environment.get('ui_timeout', 60)
        self.log_info(f"UI timeout set to {self.ui_timeout}s")
        yield


class IntegrationTest(BaseTest):
    """Base class for integration tests."""

    @pytest.fixture(autouse=True)
    def integration_setup(self):
        """Integration test setup."""
        self.log_info("Integration test context initialized")
        yield
