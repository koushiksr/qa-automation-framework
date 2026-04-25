"""
Test history tracking system.
Tracks pass/fail rates, execution times, and trends across runs.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from src.config.settings import settings


class TestHistoryTracker:
    """
    Tracks test execution history across runs.
    Stores: pass/fail status, execution time, timestamps, markers.
    """

    def __init__(self):
        self.history_file = Path(settings.reporting.get(
            'history_file', 'reports/history/test_history.json'
        ))
        self.current_run_results: List[dict] = []
        self._ensure_history_file()

    def _ensure_history_file(self):
        """Create history file if it doesn't exist."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self._save_history([])

    def _load_history(self) -> List[dict]:
        """Load history from file."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_history(self, history: List[dict]):
        """Save history to file."""
        max_runs = settings.reporting.get('max_history_runs', 100)
        with open(self.history_file, 'w') as f:
            json.dump(history[-max_runs:], f, indent=2, default=str)

    def add_result(self, test_name: str, status: str, duration: float,
                   markers: List[str] = None, error: str = None):
        """Add a test result to current run."""
        self.current_run_results.append({
            'name': test_name,
            'status': status,
            'duration': round(duration, 3),
            'markers': markers or [],
            'error': error,
            'timestamp': datetime.now().isoformat()
        })

    def save_run(self, exit_status: int):
        """Save current run results to history."""
        history = self._load_history()

        summary = self._calculate_summary(self.current_run_results)

        run_data = {
            'run_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'run_time': datetime.now().isoformat(),
            'exit_status': exit_status,
            'summary': summary,
            'tests': self.current_run_results
        }

        history.append(run_data)
        self._save_history(history)
        self.current_run_results = []

    def _calculate_summary(self, results: List[dict]) -> dict:
        """Calculate summary statistics for a run."""
        total = len(results)
        passed = len([r for r in results if r['status'] == 'passed'])
        failed = len([r for r in results if r['status'] == 'failed'])
        skipped = len([r for r in results if r['status'] == 'skipped'])
        total_duration = sum(r['duration'] for r in results)

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'pass_rate': round((passed / total * 100) if total > 0 else 0, 2),
            'total_duration': round(total_duration, 2),
            'avg_duration': round((total_duration / total) if total > 0 else 0, 3)
        }

    def get_test_history(self, test_name: str) -> List[dict]:
        """Get all historical results for a specific test."""
        history = self._load_history()
        results = []
        for run in history:
            for test in run.get('tests', []):
                if test['name'] == test_name:
                    results.append({
                        'run_id': run['run_id'],
                        'run_time': run['run_time'],
                        **test
                    })
        return results

    def get_test_statistics(self, test_name: str) -> dict:
        """Get aggregated statistics for a specific test."""
        history = self.get_test_history(test_name)
        if not history:
            return {'message': 'No history found'}

        total = len(history)
        passed = len([h for h in history if h['status'] == 'passed'])
        failed = len([h for h in history if h['status'] == 'failed'])
        durations = [h['duration'] for h in history]

        return {
            'test_name': test_name,
            'total_runs': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': round((passed / total * 100), 2),
            'avg_duration': round(sum(durations) / len(durations), 3),
            'min_duration': round(min(durations), 3),
            'max_duration': round(max(durations), 3),
            'last_status': history[-1]['status'],
            'last_run': history[-1]['run_time']
        }

    def get_category_statistics(self, category: str) -> dict:
        """Get statistics for tests with a specific marker/category."""
        history = self._load_history()
        results = []

        for run in history:
            for test in run.get('tests', []):
                if category in test.get('markers', []):
                    results.append(test)

        if not results:
            return {'message': f'No history found for category: {category}'}

        total = len(results)
        passed = len([r for r in results if r['status'] == 'passed'])
        durations = [r['duration'] for r in results]

        return {
            'category': category,
            'total_runs': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': round((passed / total * 100), 2),
            'avg_duration': round(sum(durations) / len(durations), 3)
        }

    def get_trend_data(self, last_n_runs: int = 10) -> dict:
        """Get trend data for the last N runs."""
        history = self._load_history()[-last_n_runs:]

        trends = {
            'run_ids': [],
            'pass_rates': [],
            'durations': [],
            'total_tests': [],
            'failed_tests': []
        }

        for run in history:
            summary = run.get('summary', {})
            trends['run_ids'].append(run.get('run_id', 'unknown'))
            trends['pass_rates'].append(summary.get('pass_rate', 0))
            trends['durations'].append(summary.get('total_duration', 0))
            trends['total_tests'].append(summary.get('total', 0))
            trends['failed_tests'].append(summary.get('failed', 0))

        return trends

    def get_flaky_tests(self, threshold: float = 50.0) -> List[dict]:
        """
        Identify flaky tests (tests with inconsistent results).
        Returns tests with pass rate between threshold and (100 - threshold).
        """
        history = self._load_history()
        test_results = defaultdict(list)

        for run in history:
            for test in run.get('tests', []):
                test_results[test['name']].append(test['status'])

        flaky = []
        for test_name, statuses in test_results.items():
            if len(statuses) >= 3:  # Need at least 3 runs to determine flakiness
                passed = len([s for s in statuses if s == 'passed'])
                pass_rate = (passed / len(statuses)) * 100
                if threshold < pass_rate < (100 - threshold):
                    flaky.append({
                        'name': test_name,
                        'total_runs': len(statuses),
                        'passed': passed,
                        'failed': len(statuses) - passed,
                        'pass_rate': round(pass_rate, 2)
                    })

        return sorted(flaky, key=lambda x: abs(50 - x['pass_rate']))


# Global tracker instance
history_tracker = TestHistoryTracker()


def get_history_tracker() -> TestHistoryTracker:
    """Get the global history tracker instance."""
    return history_tracker
