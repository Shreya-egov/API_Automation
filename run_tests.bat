@echo off
REM ###############################################################################
REM API Automation Test Suite Runner (Windows)
REM This script runs the complete test suite and generates Allure reports
REM ###############################################################################

echo ===========================================
echo API Automation Test Suite Runner
echo ===========================================
echo.

REM Step 1: Clean previous results
echo Step 1: Cleaning previous test results...
if exist allure-results rmdir /s /q allure-results
if exist allure-report rmdir /s /q allure-report
echo [DONE] Previous results cleaned
echo.

REM Step 2: Run test suite
echo Step 2: Running test suite...
pytest tests/ --alluredir=allure-results --clean-alluredir -v -x
set TEST_EXIT_CODE=%ERRORLEVEL%

if %TEST_EXIT_CODE% NEQ 0 (
    echo [ERROR] Tests failed with exit code: %TEST_EXIT_CODE%
    echo [INFO] Continuing to generate report...
) else (
    echo [SUCCESS] All tests passed successfully!
)
echo.

REM Step 3: Copy categories
echo Step 3: Copying Allure categories configuration...
copy categories.json allure-results\
echo [DONE] Categories copied
echo.

REM Step 4: Generate Allure report
echo Step 4: Generating Allure HTML report...
allure generate allure-results --clean -o allure-report
echo [DONE] Report generated successfully
echo.

REM Step 5: Display test results summary
echo Step 5: Test Results Summary
if exist output\ids.txt (
    for /f "tokens=*" %%a in ('findstr "Hierarchy Type:" output\ids.txt') do set LATEST_HIERARCHY=%%a
    echo %LATEST_HIERARCHY%
)
echo.

REM Step 6: Start HTTP server and open report
echo Step 6: Starting HTTP server for Allure report...
echo Report will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Kill any existing server on port 8000
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *http.server*" 2>nul

REM Start server
cd allure-report
start /B python -m http.server 8000

REM Wait for server to start
timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:8000

echo.
echo ===========================================
echo Test Execution Complete!
echo ===========================================
echo.
echo Summary:
echo   - Test Results: allure-results/
echo   - HTML Report: allure-report/
echo   - Report URL: http://localhost:8000
echo   - Generated IDs: output/ids.txt
echo.
echo To stop the server: Close this window or press Ctrl+C
echo.

pause
exit /b %TEST_EXIT_CODE%
