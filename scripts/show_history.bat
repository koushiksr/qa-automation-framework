@echo off
REM =============================================================================
REM Show Test History Summary
REM Usage: show_history.bat [test_name|category_name]
REM =============================================================================

setlocal

set PYTHON_EXE=venv\Scripts\python.exe
set PROJECT_DIR=%~dp0..

cd /d "%PROJECT_DIR%"

if "%~1"=="" goto :show_summary

REM Check if argument is a category or test name
"%PYTHON_EXE%" -c "from src.utils.test_history import get_history_tracker; t = get_history_tracker(); print(t.get_test_statistics('%~1') if '%~1' in open('reports/history/test_history.json').read() else t.get_category_statistics('%~1'))"
goto :end

:show_summary
"%PYTHON_EXE%" -c "from src.utils.test_history import get_history_tracker; import json; t = get_history_tracker(); h = t._load_history(); print(f'Total runs: {len(h)}'); print(json.dumps(t.get_trend_data(), indent=2) if h else 'No history yet')"

:end
endlocal
