@echo off
REM =============================================================================
REM View Test Reports
REM Usage: view_report.bat [allure|html|history]
REM =============================================================================

setlocal

set PROJECT_DIR=%~dp0..
set ALLURE_REPORT=%PROJECT_DIR%\reports\allure-report
set HTML_REPORT=%PROJECT_DIR%\reports\html\latest.html
set HISTORY_FILE=%PROJECT_DIR%\reports\history\test_history.json

REM Default to showing all
set REPORT_TYPE=%~1
if "%REPORT_TYPE%"=="" set REPORT_TYPE=all

if /i "%REPORT_TYPE%"=="allure" goto :open_allure
if /i "%REPORT_TYPE%"=="html" goto :open_html
if /i "%REPORT_TYPE%"=="history" goto :view_history
if /i "%REPORT_TYPE%"=="all" goto :open_all

echo Invalid report type: %REPORT_TYPE%
echo Valid options: allure, html, history, all
goto :end

:open_allure
echo Opening Allure report...
if exist "%ALLURE_REPORT%" (
    start "" "%ALLURE_REPORT%\index.html"
    echo Allure report opened in browser
) else (
    echo Allure report not found. Run tests first.
)
goto :end

:open_html
echo Opening HTML report...
if exist "%HTML_REPORT%" (
    start "" "%HTML_REPORT%"
    echo HTML report opened in browser
) else (
    echo HTML report not found. Run tests first.
)
goto :end

:view_history
echo ============================================================================
echo Test History
echo ============================================================================
if exist "%HISTORY_FILE%" (
    type "%HISTORY_FILE%"
) else (
    echo History file not found. Run tests first.
)
goto :end

:open_all
echo Opening all reports...
if exist "%ALLURE_REPORT%" (
    start "" "%ALLURE_REPORT%\index.html"
    echo Allure report opened
) else (
    echo Allure report not found
)
if exist "%HTML_REPORT%" (
    start "" "%HTML_REPORT%"
    echo HTML dashboard opened
) else (
    echo HTML dashboard not found
)
goto :end

:end
endlocal
