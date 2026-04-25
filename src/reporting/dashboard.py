"""
HTML Dashboard Report Generator.
Creates interactive HTML reports with charts, history, and category breakdowns.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from src.config.settings import settings
from src.utils.test_history import get_history_tracker


class DashboardGenerator:
    """Generates interactive HTML dashboard for test results."""

    def __init__(self):
        self.history_tracker = get_history_tracker()
        self.output_dir = Path(settings.reporting.get(
            'html_report_dir', 'reports/html'
        ))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, current_run: Dict = None):
        """Generate the full HTML dashboard."""
        history = self.history_tracker._load_history()
        trend_data = self.history_tracker.get_trend_data()
        flaky_tests = self.history_tracker.get_flaky_tests()

        # Get category statistics
        categories = ['smoke', 'regression', 'critical', 'api', 'ui', 'integration', 'performance']
        category_stats = {}
        for cat in categories:
            cat_data = self.history_tracker.get_category_statistics(cat)
            if 'message' not in cat_data:
                category_stats[cat] = cat_data

        # Get latest run summary
        latest_summary = {}
        if history:
            latest_summary = history[-1].get('summary', {})

        html_content = self._build_html(
            latest_summary=latest_summary,
            trend_data=trend_data,
            category_stats=category_stats,
            flaky_tests=flaky_tests,
            history=history,
            current_run=current_run
        )

        output_file = self.output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Also create latest.html as a symlink/copy
        latest_file = self.output_dir / "latest.html"
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(output_file)

    def _build_html(self, latest_summary: Dict, trend_data: Dict,
                    category_stats: Dict, flaky_tests: List,
                    history: List, current_run: Dict = None) -> str:
        """Build the HTML content for the dashboard."""

        # Use current run if provided, otherwise use latest from history
        summary = current_run.get('summary', latest_summary) if current_run else latest_summary

        # Build test results table from latest run
        test_rows = ""
        if current_run and 'tests' in current_run:
            for test in current_run['tests']:
                status_class = test['status']
                markers_html = ''.join([
                    f'<span class="marker marker-{m}">{m}</span>'
                    for m in test.get('markers', [])
                ])
                error_html = f'<div class="error">{test.get("error", "")}</div>' if test.get('error') else ''
                test_rows += f"""
                <tr class="test-row {status_class}">
                    <td>{test['name']}</td>
                    <td>{markers_html}</td>
                    <td>{test['status']}</td>
                    <td>{test['duration']:.3f}s</td>
                    <td>{datetime.fromisoformat(test['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
                {error_html}
                """
        elif history:
            latest_tests = history[-1].get('tests', [])
            for test in latest_tests:
                status_class = test['status']
                markers_html = ''.join([
                    f'<span class="marker marker-{m}">{m}</span>'
                    for m in test.get('markers', [])
                ])
                error_html = f'<div class="error">{test.get('error', '')}</div>' if test.get('error') else ''
                test_rows += f"""
                <tr class="test-row {status_class}">
                    <td>{test['name']}</td>
                    <td>{markers_html}</td>
                    <td>{test['status']}</td>
                    <td>{test['duration']:.3f}s</td>
                    <td>{datetime.fromisoformat(test['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
                {error_html}
                """

        # Build trend chart data
        trend_labels = json.dumps(trend_data.get('run_ids', []))
        pass_rate_data = json.dumps(trend_data.get('pass_rates', []))
        duration_data = json.dumps(trend_data.get('durations', []))

        # Build category stats table
        category_rows = ""
        for cat, stats in category_stats.items():
            pass_rate = stats.get('pass_rate', 0)
            color = '#4caf50' if pass_rate >= 90 else '#ff9800' if pass_rate >= 70 else '#f44336'
            category_rows += f"""
            <tr>
                <td>{cat}</td>
                <td>{stats.get('total_runs', 0)}</td>
                <td>{stats.get('passed', 0)}</td>
                <td>{stats.get('failed', 0)}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress" style="width: {pass_rate}%; background: {color}"></div>
                    </div>
                    {pass_rate}%
                </td>
                <td>{stats.get('avg_duration', 0):.3f}s</td>
            </tr>
            """

        # Build flaky tests table
        flaky_rows = ""
        for test in flaky_tests[:10]:  # Show top 10
            flaky_rows += f"""
            <tr>
                <td>{test['name']}</td>
                <td>{test['total_runs']}</td>
                <td>{test['passed']}</td>
                <td>{test['failed']}</td>
                <td>{test['pass_rate']}%</td>
            </tr>
            """

        # Run history table
        history_rows = ""
        for run in reversed(history[-10:]):
            run_summary = run.get('summary', {})
            history_rows += f"""
            <tr>
                <td>{run.get('run_id', 'N/A')}</td>
                <td>{datetime.fromisoformat(run['run_time']).strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{run_summary.get('total', 0)}</td>
                <td class="passed">{run_summary.get('passed', 0)}</td>
                <td class="failed">{run_summary.get('failed', 0)}</td>
                <td>{run_summary.get('skipped', 0)}</td>
                <td>{run_summary.get('pass_rate', 0)}%</td>
                <td>{run_summary.get('total_duration', 0):.2f}s</td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        h1 {{ text-align: center; padding: 20px; color: #00d9ff; }}
        h2 {{ color: #00d9ff; margin: 20px 0 10px; border-bottom: 2px solid #00d9ff; padding-bottom: 5px; }}

        .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .card {{ background: #16213e; border-radius: 10px; padding: 20px; text-align: center; }}
        .card h3 {{ color: #888; font-size: 14px; margin-bottom: 10px; }}
        .card .value {{ font-size: 36px; font-weight: bold; }}
        .card.total .value {{ color: #00d9ff; }}
        .card.passed .value {{ color: #4caf50; }}
        .card.failed .value {{ color: #f44336; }}
        .card.skipped .value {{ color: #ff9800; }}
        .card.duration .value {{ color: #9c27b0; }}
        .card.pass-rate .value {{ color: #00e676; }}

        .chart-container {{ background: #16213e; border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .chart-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 900px) {{ .chart-row {{ grid-template-columns: 1fr; }} }}

        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: #16213e; border-radius: 10px; overflow: hidden; }}
        th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #00d9ff; font-weight: 600; }}
        tr:hover {{ background: #1a3a5c; }}
        .passed {{ color: #4caf50; }}
        .failed {{ color: #f44336; }}
        .skipped {{ color: #ff9800; }}

        .marker {{ display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 12px; font-size: 12px; background: #0f3460; }}
        .marker-smoke {{ background: #e91e63; }}
        .marker-regression {{ background: #9c27b0; }}
        .marker-critical {{ background: #f44336; }}
        .marker-api {{ background: #2196f3; }}
        .marker-ui {{ background: #4caf50; }}
        .marker-integration {{ background: #ff9800; }}
        .marker-performance {{ background: #673ab7; }}

        .progress-bar {{ width: 100%; height: 20px; background: #0f3460; border-radius: 10px; overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 10px; }}
        .progress {{ height: 100%; transition: width 0.3s; }}

        .error {{ background: #2a1a1a; color: #f44336; padding: 10px; margin: 5px 0; border-radius: 5px; font-family: monospace; font-size: 12px; }}

        .section {{ margin: 30px 0; }}
        .tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
        .tab {{ padding: 10px 20px; background: #0f3460; border: none; color: #eee; cursor: pointer; border-radius: 5px; }}
        .tab.active {{ background: #00d9ff; color: #1a1a2e; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        .flaky-warning {{ background: #2a2a1a; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Test Automation Dashboard</h1>
        <p style="text-align: center; color: #888;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="summary-cards">
            <div class="card total">
                <h3>Total Tests</h3>
                <div class="value">{summary.get('total', 0)}</div>
            </div>
            <div class="card passed">
                <h3>Passed</h3>
                <div class="value">{summary.get('passed', 0)}</div>
            </div>
            <div class="card failed">
                <h3>Failed</h3>
                <div class="value">{summary.get('failed', 0)}</div>
            </div>
            <div class="card skipped">
                <h3>Skipped</h3>
                <div class="value">{summary.get('skipped', 0)}</div>
            </div>
            <div class="card pass-rate">
                <h3>Pass Rate</h3>
                <div class="value">{summary.get('pass_rate', 0)}%</div>
            </div>
            <div class="card duration">
                <h3>Total Duration</h3>
                <div class="value">{summary.get('total_duration', 0):.1f}s</div>
            </div>
        </div>

        <div class="section">
            <h2>📈 Trend Analysis</h2>
            <div class="chart-row">
                <div class="chart-container">
                    <h3>Pass Rate Trend</h3>
                    <canvas id="passRateChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Execution Time Trend</h3>
                    <canvas id="durationChart"></canvas>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Category Statistics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Total Runs</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Pass Rate</th>
                        <th>Avg Duration</th>
                    </tr>
                </thead>
                <tbody>
                    {category_rows if category_rows else '<tr><td colspan="6">No category data available</td></tr>'}
                </tbody>
            </table>
        </div>

        {f'<div class="flaky-warning"><h3>⚠️ Flaky Tests Detected</h3><p>Found {len(flaky_tests)} tests with inconsistent results.</p></div>' if flaky_tests else ''}

        <div class="section">
            <h2>🔧 Test Results</h2>
            <div class="tabs">
                <button class="tab active" onclick="showTab('latest')">Latest Run</button>
                <button class="tab" onclick="showTab('history')">Run History</button>
                <button class="tab" onclick="showTab('flaky')">Flaky Tests</button>
            </div>

            <div id="latest" class="tab-content active">
                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Categories</th>
                            <th>Status</th>
                            <th>Duration</th>
                            <th>Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {test_rows if test_rows else '<tr><td colspan="5">No test results available</td></tr>'}
                    </tbody>
                </table>
            </div>

            <div id="history" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>Run ID</th>
                            <th>Timestamp</th>
                            <th>Total</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Skipped</th>
                            <th>Pass Rate</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows if history_rows else '<tr><td colspan="8">No run history available</td></tr>'}
                    </tbody>
                </table>
            </div>

            <div id="flaky" class="tab-content">
                <table>
                    <thead>
                        <tr>
                            <th>Test Name</th>
                            <th>Total Runs</th>
                            <th>Passed</th>
                            <th>Failed</th>
                            <th>Pass Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {flaky_rows if flaky_rows else '<tr><td colspan="5">No flaky tests detected</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        const trendLabels = {trend_labels};
        const passRateData = {pass_rate_data};
        const durationData = {duration_data};

        new Chart(document.getElementById('passRateChart'), {{
            type: 'line',
            data: {{
                labels: trendLabels,
                datasets: [{{
                    label: 'Pass Rate (%)',
                    data: passRateData,
                    borderColor: '#00d9ff',
                    backgroundColor: 'rgba(0, 217, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, max: 100, grid: {{ color: '#333' }} }},
                    x: {{ grid: {{ color: '#333' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#eee' }} }} }}
            }}
        }});

        new Chart(document.getElementById('durationChart'), {{
            type: 'bar',
            data: {{
                labels: trendLabels,
                datasets: [{{
                    label: 'Duration (s)',
                    data: durationData,
                    backgroundColor: '#9c27b0'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#333' }} }},
                    x: {{ grid: {{ color: '#333' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#eee' }} }} }}
            }}
        }});
    </script>
</body>
</html>"""
