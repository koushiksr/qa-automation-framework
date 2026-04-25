"""
Enhanced logging system with loguru.
Features: Console + file output, test-specific logs, colored output, structured logging.
"""
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from src.config.settings import settings


class TestLogger:
    """Enhanced logger for test framework with context-aware logging."""

    _instance = None
    _test_context = {}
    _configured = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def configure(self):
        """Configure loguru with console and file handlers."""
        if self._configured:
            return

        self._configured = True
        logger.remove()

        log_config = settings.logging

        # Console handler with color
        if log_config.get('console', True):
            logger.add(
                sys.stdout,
                level=log_config.get('level', 'INFO'),
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
                       "<level>{message}</level>",
                colorize=True,
                catch=True  # Catch errors to prevent crashes
            )

        # File handler
        if log_config.get('file', True):
            log_dir = Path(log_config.get('log_dir', 'reports/logs'))
            log_dir.mkdir(parents=True, exist_ok=True)

            # Main log file with rotation
            logger.add(
                log_dir / "test_{time:YYYY-MM-DD}.log",
                level=log_config.get('level', 'INFO'),
                rotation=f"{log_config.get('max_file_size_mb', 10)} MB",
                retention=f"{log_config.get('retention_days', 30)} days",
                format=log_config.get(
                    'format',
                    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {function} | {message}"
                ),
                encoding='utf-8',
                catch=True  # Catch errors to prevent crashes
            )

    def set_test_context(self, test_name: str, category: str = None):
        """Set context for current test logging."""
        self.configure()  # Ensure configured
        self._test_context = {
            'test_name': test_name,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }

    def clear_test_context(self):
        """Clear test context after test completion."""
        self._test_context = {}

    def info(self, message: str, **extra):
        self.configure()
        logger.info(self._format(message, **extra))

    def debug(self, message: str, **extra):
        self.configure()
        logger.debug(self._format(message, **extra))

    def warning(self, message: str, **extra):
        self.configure()
        logger.warning(self._format(message, **extra))

    def error(self, message: str, **extra):
        self.configure()
        logger.error(self._format(message, **extra))

    def success(self, message: str, **extra):
        self.configure()
        logger.success(self._format(message, **extra))

    def _format(self, message: str, **extra) -> str:
        """Format message with test context if available."""
        if self._test_context:
            prefix = f"[{self._test_context.get('test_name', 'unknown')}] "
            return f"{prefix}{message}"
        return message


# Global logger instance
test_logger = TestLogger()


def get_logger() -> TestLogger:
    """Get the global test logger instance."""
    return test_logger
