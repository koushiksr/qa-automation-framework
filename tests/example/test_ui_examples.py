"""
Example UI tests demonstrating framework features.
Shows: UI-specific base class, logging, timing, categories.
"""
import pytest
import time
from src.core.base_test import UITest
from src.utils.assertions import assert_equal, assert_true, assert_not_none
from src.utils.assertions import assert_less


class TestUIExamples(UITest):
    """
    Example UI tests showing framework capabilities.
    Run with: pytest -m ui -v
    """

    @pytest.mark.smoke
    @pytest.mark.ui
    def test_page_loads(self):
        """
        Smoke test: Verify page loads successfully.
        Category: smoke, ui
        """
        self.log_info("Testing page load")

        # Simulated page load
        page_title = "Test Application"
        load_time = 0.5  # Simulated

        self.log_debug(f"Page title: {page_title}")
        self.log_info(f"Page load time: {load_time}s")

        assert_not_none(page_title, "Page title should not be None")
        assert_true(len(page_title) > 0, "Page title should not be empty")

        self.log_success("Page loaded successfully")

    @pytest.mark.regression
    @pytest.mark.ui
    def test_form_submission(self):
        """
        Regression test: Verify form submission works.
        Category: regression, ui, feature_auth
        """
        self.log_info("Testing form submission")

        # Simulated form data
        form_data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }

        self.log_debug(f"Submitting form with: {form_data}")

        # Simulate form submission
        time.sleep(0.1)
        submission_success = True

        assert_true(submission_success, "Form submission should succeed")
        self.log_success("Form submitted successfully")

    @pytest.mark.ui
    @pytest.mark.critical
    def test_checkout_flow(self):
        """
        Critical test: Complete checkout flow.
        Category: critical, ui, feature_patient
        """
        self.log_info("Testing checkout flow")

        steps = [
            'Add item to cart',
            'Navigate to checkout',
            'Enter shipping info',
            'Enter payment info',
            'Complete purchase'
        ]

        for i, step in enumerate(steps, 1):
            self.log_info(f"Step {i}/{len(steps)}: {step}")
            time.sleep(0.05)  # Simulate step execution

        self.log_success("Checkout flow completed successfully")

    @pytest.mark.ui
    @pytest.mark.performance
    def test_page_render_performance(self):
        """
        Performance test: Page render time.
        Category: ui, performance
        """
        self.log_info("Testing page render performance")

        # Measure render time
        start = time.time()

        # Simulated render
        time.sleep(0.2)

        render_time = time.time() - start
        self.log_info(f"Page render time: {render_time:.3f}s")

        assert_less(render_time, 3.0, f"Page render too slow: {render_time:.3f}s")
        self.log_success("Page render performance acceptable")

    @pytest.mark.flaky
    @pytest.mark.rerun
    def test_intermittent_feature(self):
        self.log_info("Testing potentially flaky feature")

        import random
        if random.random() < 0.3:
            raise AssertionError("Intermittent failure occurred")

        self.log_success("Flaky test passed this time")