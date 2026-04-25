@echo off
REM =============================================================================
REM Test Runner Script
REM Usage: run_tests.bat [options]
REM =============================================================================

setlocal EnableDelayedExpansion

REM Configuration
set PYTHON_EXE=venv\Scripts\python.exe
set PROJECT_DIR=%~dp0..
set ALLURE_RESULTS=%PROJECT_DIR%\reports\allure-results
set ALLURE_REPORT=%PROJECT_DIR%\reports\allure-report
set ALLURE_HISTORY_TMP=%PROJECT_DIR%\reports\allure-history-tmp
set HTML_REPORT=%PROJECT_DIR%\reports\html

REM Default options
set TEST_MARKER=
set TEST_FILE=
set EXTRA_ARGS=-v --tb=short

REM Parse arguments
:parse_args
if "%~1"=="" goto :end_parse
if /i "%~1"=="smoke" set TEST_MARKER=-m smoke && shift && goto :parse_args
if /i "%~1"=="regression" set TEST_MARKER=-m regression && shift && goto :parse_args
if /i "%~1"=="critical" set TEST_MARKER=-m critical && shift && goto :parse_args
if /i "%~1"=="api" set TEST_MARKER=-m api && shift && goto :parse_args
if /i "%~1"=="ui" set TEST_MARKER=-m ui && shift && goto :parse_args
if /i "%~1"=="integration" set TEST_MARKER=-m integration && shift && goto :parse_args
if /i "%~1"=="parallel" set EXTRA_ARGS=!EXTRA_ARGS! -n auto && shift && goto :parse_args
if /i "%~1"=="rerun" set EXTRA_ARGS=!EXTRA_ARGS! --reruns 2 && shift && goto :parse_args
if /i "%~1"=="verbose" set EXTRA_ARGS=!EXTRA_ARGS! -vv && shift && goto :parse_args
if /i "%~1"=="help" goto :help
if "%~1"=="" goto :end_parse
set TEST_FILE=%~1 && shift && goto :parse_args

:end_parse

REM Clean previous results
echo ============================================================================
echo Cleaning previous test results...
echo ============================================================================
REM Preserve allure history before cleaning results
if exist "%ALLURE_HISTORY_TMP%" rmdir /s /q "%ALLURE_HISTORY_TMP%"
if exist "%ALLURE_REPORT%\history" (
    echo Preserving Allure history from previous report...
    xcopy "%ALLURE_REPORT%\history" "%ALLURE_HISTORY_TMP%\" /E /I /Y >nul
)
if exist "%ALLURE_RESULTS%" rmdir /s /q "%ALLURE_RESULTS%"
mkdir "%ALLURE_RESULTS%"
if exist "%ALLURE_HISTORY_TMP%" (
    echo Restoring Allure history into new results...
    xcopy "%ALLURE_HISTORY_TMP%" "%ALLURE_RESULTS%\history\" /E /I /Y >nul
    rmdir /s /q "%ALLURE_HISTORY_TMP%"
)

REM Run tests
echo ============================================================================
echo Running Pytest Tests
echo ============================================================================
echo Test marker: %TEST_MARKER%
echo Test file: %TEST_FILE%
echo Extra args: %EXTRA_ARGS%
echo.

cd /d "%PROJECT_DIR%"
"%PYTHON_EXE%" -m pytest %TEST_MARKER% %TEST_FILE% %EXTRA_ARGS% --alluredir="%ALLURE_RESULTS%" --html="%HTML_REPORT%\latest_run.html" --self-contained-html

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================================
    echo Tests completed successfully!
    echo ============================================================================
) else (
    echo.
    echo ============================================================================
    echo Tests failed with exit code: %ERRORLEVEL%
    echo ============================================================================
)

REM Generate Allure report
echo.
echo ============================================================================
echo Generating Allure Report...
echo ============================================================================
call allure generate "%ALLURE_RESULTS%" -o "%PROJECT_DIR%\reports\allure-report" --clean

echo.
echo ============================================================================
echo Reports generated:
echo   HTML Report: %HTML_REPORT%\latest_run.html
echo   Allure Report: %PROJECT_DIR%\reports\allure-report
echo ============================================================================
echo.
echo To view Allure report, run: scripts\view_report.bat
echo.

goto :end

:help
echo Usage: run_tests.bat [options] [test_file]
echo.
echo Options:
echo   smoke       Run only smoke tests
echo   regression  Run only regression tests
echo   critical    Run only critical tests
echo   api         Run only API tests
echo   ui          Run only UI tests
echo   integration Run only integration tests
echo   parallel    Run tests in parallel
echo   rerun       Rerun failed tests (2 attempts)
echo   verbose     Extra verbose output
echo   help        Show this help message
echo.
echo Examples:
echo   run_tests.bat smoke
echo   run_tests.bat api parallel
echo   run_tests.bat tests\example\test_api_examples.py
goto :end

:end
endlocal
