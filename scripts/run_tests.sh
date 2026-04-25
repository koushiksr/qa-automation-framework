#!/bin/bash

echo "Running tests..."
pytest pytest --alluredir=reports/allure-results
echo "Report generated at reports/allure-report"