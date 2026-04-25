"""
Enhanced assertion utilities with better error messages.
"""
import pytest


def assert_equal(actual, expected, message: str = None):
    """
    Assert two values are equal with enhanced error message.

    Args:
        actual: Actual value
        expected: Expected value
        message: Optional custom message

    Raises:
        AssertionError: If values are not equal
    """
    if message:
        assert actual == expected, f"{message}: expected {expected!r}, got {actual!r}"
    else:
        assert actual == expected, f"Assertion failed: expected {expected!r}, got {actual!r}"


def assert_not_equal(actual, expected, message: str = None):
    """Assert two values are not equal."""
    if message:
        assert actual != expected, f"{message}: expected not {expected!r}, but got {actual!r}"
    else:
        assert actual != expected, f"Assertion failed: expected not {expected!r}, but got {actual!r}"


def assert_in(item, container, message: str = None):
    """
    Assert item is in container.

    Args:
        item: Item to find
        container: Container (list, dict, string, etc.)
        message: Optional custom message
    """
    if message:
        assert item in container, f"{message}: {item!r} not found in {container!r}"
    else:
        assert item in container, f"Assertion failed: {item!r} not found in {container!r}"


def assert_not_in(item, container, message: str = None):
    """Assert item is not in container."""
    if message:
        assert item not in container, f"{message}: {item!r} should not be in {container!r}"
    else:
        assert item not in container, f"Assertion failed: {item!r} should not be in {container!r}"


def assert_true(condition, message: str = None):
    """
    Assert condition is True.

    Args:
        condition: Boolean condition
        message: Optional custom message
    """
    if message:
        assert condition, f"{message}: condition was False"
    else:
        assert condition, f"Assertion failed: expected True, got False"


def assert_false(condition, message: str = None):
    """Assert condition is False."""
    if message:
        assert not condition, f"{message}: condition was True"
    else:
        assert not condition, f"Assertion failed: expected False, got True"


def assert_none(value, message: str = None):
    """Assert value is None."""
    if message:
        assert value is None, f"{message}: expected None, got {value!r}"
    else:
        assert value is None, f"Assertion failed: expected None, got {value!r}"


def assert_not_none(value, message: str = None):
    """Assert value is not None."""
    if message:
        assert value is not None, f"{message}: expected non-None value"
    else:
        assert value is not None, f"Assertion failed: expected non-None value, got None"


def assert_greater(a, b, message: str = None):
    """Assert a > b."""
    if message:
        assert a > b, f"{message}: expected {a!r} > {b!r}"
    else:
        assert a > b, f"Assertion failed: expected {a!r} > {b!r}"


def assert_less(a, b, message: str = None):
    """Assert a < b."""
    if message:
        assert a < b, f"{message}: expected {a!r} < {b!r}"
    else:
        assert a < b, f"Assertion failed: expected {a!r} < {b!r}"


def assert_almost_equal(a, b, tolerance: float = 0.001, message: str = None):
    """Assert two floats are approximately equal."""
    diff = abs(a - b)
    if message:
        assert diff <= tolerance, f"{message}: |{a} - {b}| = {diff} > {tolerance}"
    else:
        assert diff <= tolerance, f"Assertion failed: |{a} - {b}| = {diff} > {tolerance}"


def assert_raises(exception_type, func, *args, **kwargs):
    """
    Assert that a function raises a specific exception.

    Usage:
        assert_raises(ValueError, int, "not_a_number")
    """
    try:
        func(*args, **kwargs)
    except exception_type:
        return True
    except Exception as e:
        raise AssertionError(
            f"Expected {exception_type.__name__}, but got {type(e).__name__}: {e}"
        )
    raise AssertionError(f"Expected {exception_type.__name__}, but no exception was raised")
