#!/bin/bash

###############################################################################
# API Automation Test Suite Runner
# This script runs the complete test suite and generates Allure reports
###############################################################################

set -e  # Exit on error

echo "==========================================="
echo "API Automation Test Suite Runner"
echo "==========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Clean previous results
echo -e "${BLUE}Step 1: Cleaning previous test results...${NC}"
rm -rf allure-results/ allure-report/
echo -e "${GREEN}✓ Previous results cleaned${NC}"
echo ""

# Step 2: Run test suite
echo -e "${BLUE}Step 2: Running test suite...${NC}"
pytest tests/ --alluredir=allure-results --clean-alluredir -v

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo -e "${RED}✗ Tests failed with exit code: $TEST_EXIT_CODE${NC}"
    echo -e "${YELLOW}Continuing to generate report...${NC}"
else
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
fi
echo ""

# Step 3: Copy categories
echo -e "${BLUE}Step 3: Copying Allure categories configuration...${NC}"
cp categories.json allure-results/
echo -e "${GREEN}✓ Categories copied${NC}"
echo ""

# Step 4: Generate Allure report
echo -e "${BLUE}Step 4: Generating Allure HTML report...${NC}"
allure generate allure-results --clean -o allure-report
echo -e "${GREEN}✓ Report generated successfully${NC}"
echo ""

# Step 5: Display test results summary
echo -e "${BLUE}Step 5: Test Results Summary${NC}"
if [ -f "output/ids.txt" ]; then
    LATEST_HIERARCHY=$(grep "Hierarchy Type:" output/ids.txt | tail -1)
    echo -e "${GREEN}$LATEST_HIERARCHY${NC}"
fi
echo ""

# Step 6: Start HTTP server and open report
echo -e "${BLUE}Step 6: Starting HTTP server for Allure report...${NC}"
echo -e "${YELLOW}Report will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Kill any existing server on port 8000
pkill -f "python3 -m http.server 8000" 2>/dev/null || true

# Start server and open browser
cd allure-report
python3 -m http.server 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 2

# Open browser
xdg-open http://localhost:8000 2>/dev/null || echo "Please open http://localhost:8000 in your browser"

echo ""
echo "==========================================="
echo -e "${GREEN}Test Execution Complete!${NC}"
echo "==========================================="
echo ""
echo "Summary:"
echo "  - Test Results: allure-results/"
echo "  - HTML Report: allure-report/"
echo "  - Report URL: http://localhost:8000"
echo "  - Generated IDs: output/ids.txt"
echo ""
echo -e "${YELLOW}To stop the server: pkill -f 'python3 -m http.server 8000'${NC}"
echo ""

# Wait for user to stop (or server process)
wait $SERVER_PID 2>/dev/null

exit $TEST_EXIT_CODE
