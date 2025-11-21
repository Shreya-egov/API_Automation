# API Automation Framework

A comprehensive Python-based API automation testing framework for boundary management and localization services using pytest.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Test Suite](#test-suite)
- [Running Tests](#running-tests)
- [Template Automation](#template-automation)
- [Reporting](#reporting)
- [Utilities Documentation](#utilities-documentation)
- [Troubleshooting](#troubleshooting)

---

## Overview

This framework is designed to test boundary management and localization microservices with a focus on:
- **Sequential Test Execution**: 15 tests covering complete boundary management workflow
- **Template Automation**: Automated template download, data population, and upload
- **Modularity**: Reusable utilities for authentication, API calls, and data management
- **Maintainability**: Separation of test logic, payloads, and configuration
- **Reporting**: Multiple reporting formats (HTML, Allure)

---

## Project Structure

```
API_Automation/
├── tests/                                  # Test modules (sequential execution)
│   ├── test_01_boundary_hierarchy_create.py
│   ├── test_02_boundary_hierarchy_search.py
│   ├── test_03_localization_upsert.py
│   ├── test_04_localization_search.py
│   ├── test_05_generate_data.py
│   ├── test_06_generate_search.py
│   ├── test_07_file_download.py
│   ├── test_08_file_upload.py
│   ├── test_09_process_data.py
│   ├── test_10_process_search.py
│   ├── test_11_file_download_processed.py
│   ├── test_12_localization_search_french.py
│   ├── test_13_localization_search_portuguese.py
│   ├── test_14_localization_search_english.py
│   └── test_15_boundary_relationship_search.py
├── utils/                                  # Utility modules
│   ├── api_client.py                      # HTTP client wrapper
│   ├── auth.py                            # Authentication token management
│   ├── config.py                          # Configuration loader
│   ├── data_loader.py                     # Payload loader
│   ├── request_info.py                    # Request metadata builder
│   └── sample_boundary.xlsx               # Reference sample boundary data (NEVER modify)
├── payloads/                               # JSON payload templates
│   ├── boundary_hierarchy/
│   │   └── create_hierarchy.json         # Hierarchy definition (7-level structure)
│   ├── boundary_management/
│   │   ├── generate_search.json          # Search generation status
│   │   └── process_data.json             # Process uploaded boundary data
│   ├── boundary_relationships/
│   │   └── search_relationships.json     # Search boundary relationships
│   └── localization/
│       └── upsert.json                    # Upsert localization messages
├── output/                                 # Test outputs (generated at runtime)
│   ├── .gitkeep                           # Keep directory in git
│   ├── ids.txt                            # Generated hierarchy types and IDs
│   ├── template_downloaded.xlsx           # Downloaded boundary template
│   └── sample_boundary.xlsx               # Prepared file for upload
├── reports/                                # Test reports (excluded from git)
│   └── report.html                        # HTML test report
├── logs/                                   # Test execution logs (excluded from git)
│   ├── README.md                          # Logs documentation
│   └── *.log                              # Log files
├── allure-results/                         # Allure test results (excluded from git)
├── allure-report/                          # Allure HTML report (excluded from git)
├── prepare_template_for_upload.py         # Template automation script
├── .env                                   # Environment configuration (NOT in git - you must create this)
├── .gitignore                             # Git ignore rules
├── pytest.ini                             # Pytest configuration
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

---

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager
- **Virtual Environment**: Recommended for dependency isolation
- **Git**: For version control
- **openpyxl**: For Excel file operations

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Shreya-egov/API_Automation.git
cd API_Automation
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install python-dotenv requests pytest pytest-html pytest-metadata allure-pytest openpyxl
```

### 4. Configure Environment

**IMPORTANT**: Create a `.env` file in the project root directory. This file is **NOT** included in the repository for security reasons (it's excluded via `.gitignore`).

Create `.env` file manually:

```bash
# Create the file
touch .env
```

Add the following configuration to your `.env` file:

```env
# API Configuration
BASE_URL=https://unified-qa.digit.org
USERNAME=your_username
PASSWORD=your_password
TENANTID=mz
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic <base64_encoded_credentials>

# Localization Configuration
LOCALE=en_MZ
LOCALE_FRENCH=fr_MZ
LOCALE_PORTUGUESE=pt_MZ

# Search Configuration
SEARCH_LIMIT=200
SEARCH_OFFSET=0
```

**⚠️ Security Notes:**
- **NEVER commit the `.env` file to git** (it's already in `.gitignore`)
- Replace `your_username` and `your_password` with actual credentials
- Replace `<base64_encoded_credentials>` with proper encoded client credentials
- Keep this file secure and don't share it publicly

### 5. Verify Setup

```bash
pytest tests/test_01_boundary_hierarchy_create.py -v
```

---

## Configuration

### Environment Variables (.env)

**⚠️ The `.env` file is NOT tracked in git** (excluded via `.gitignore` for security). You must create it manually on each environment.

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `BASE_URL` | API base URL | `https://unified-qa.digit.org` | Yes |
| `USERNAME` | API username | `MDMSMZ` | Yes |
| `PASSWORD` | API password | `eGov@1234` | Yes |
| `TENANTID` | Tenant identifier | `mz` | Yes |
| `USERTYPE` | User type | `EMPLOYEE` | Yes |
| `CLIENT_AUTH_HEADER` | Basic auth header for OAuth | `Basic ZWdvdi11c2VyLWNsaWVudDo=` | Yes |
| `LOCALE` | Default locale for localization tests | `en_MZ` | Yes |
| `LOCALE_FRENCH` | French locale | `fr_MZ` | Yes |
| `LOCALE_PORTUGUESE` | Portuguese locale | `pt_MZ` | Yes |
| `SEARCH_LIMIT` | Default search limit | `200` | No (default: 100) |
| `SEARCH_OFFSET` | Default search offset | `0` | No (default: 0) |

### Pytest Configuration (pytest.ini)

```ini
[pytest]
pythonpath = .
```

This ensures the root directory is in the Python path for imports.

---

## Test Suite

### Test Execution Flow

The test suite consists of 15 sequential tests that validate the complete boundary management workflow:

| # | Test Name | Description | Dependencies |
|---|-----------|-------------|--------------|
| 01 | Boundary Hierarchy Create | Create 7-level boundary hierarchy (COUNTRY → PROVINCE → DISTRICT → POST ADMINISTRATIVE → LOCALITY → HEALTH FACILITY → VILLAGE) | None |
| 02 | Boundary Hierarchy Search | Verify created hierarchy exists | Test 01 |
| 03 | Localization Upsert | Upsert localization messages for boundary types | Test 01 |
| 04 | Localization Search | Search and validate localization messages | Test 03 |
| 05 | Generate Data | Trigger boundary template generation | Test 01 |
| 06 | Generate Search | Check generation status until completed | Test 05 |
| 07 | File Download | Download generated template from S3 | Test 06 |
| 08 | File Upload | Upload populated boundary data template | Test 07 |
| 09 | Process Data | Process uploaded boundary data | Test 08 |
| 10 | Process Search | Check processing status | Test 09 |
| 11 | File Download Processed | Download processed boundary file | Test 10 |
| 12 | Localization Search French | Validate French localization | Test 03 |
| 13 | Localization Search Portuguese | Validate Portuguese localization | Test 03 |
| 14 | Localization Search English | Validate English localization | Test 03 |
| 15 | Boundary Relationship Search | Search boundary hierarchical relationships | Test 09 |

### Boundary Hierarchy Structure

The tests create and validate a 7-level boundary hierarchy:

```
COUNTRY (Level 1)
└── PROVINCE (Level 2)
    └── DISTRICT (Level 3)
        └── POST ADMINISTRATIVE (Level 4)
            └── LOCALITY (Level 5)
                └── HEALTH FACILITY (Level 6)
                    └── VILLAGE (Level 7)
```

**Important**: All boundary types use UPPERCASE naming for consistency. The `create_hierarchy.json` payload defines this structure.

### Key Test Features

1. **Dynamic Hierarchy Generation**: Each test run creates a unique hierarchy type (e.g., `TEST_D35387CC`)
2. **ID Tracking**: Generated IDs stored in `output/ids.txt` for cross-test references
3. **Template Automation**: Automated download, population, and upload of boundary templates
4. **Multi-language Support**: Localization testing in English, French, and Portuguese
5. **Status Polling**: Tests wait for asynchronous operations to complete

---

## Running Tests

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run complete test suite
pytest tests/ -v

# Run with output visible
pytest tests/ -s

# Run with HTML report
pytest tests/ --html=reports/report.html --self-contained-html
```

### Run Specific Tests

```bash
# Run single test
pytest tests/test_01_boundary_hierarchy_create.py -v

# Run specific test function
pytest tests/test_01_boundary_hierarchy_create.py::test_boundary_hierarchy_create -v

# Run tests 1-8 only
pytest tests/test_01_boundary_hierarchy_create.py tests/test_02_boundary_hierarchy_search.py tests/test_03_localization_upsert.py tests/test_04_localization_search.py tests/test_05_generate_data.py tests/test_06_generate_search.py tests/test_07_file_download.py tests/test_08_file_upload.py -v
```

### Fresh Test Run (Recommended)

Clear previous test data before running:

```bash
# Clear output directory (keeps .gitkeep)
rm -f output/ids.txt output/*.xlsx

# Run tests
pytest tests/ -v --html=reports/report.html --self-contained-html
```

### Test Execution Notes

1. **Sequential Execution**: Tests must run in order (01 → 15) due to dependencies
2. **Test 08 Preparation**: Run `prepare_template_for_upload.py` before Test 08 to populate the template
3. **Test 11 Skipping**: May skip if processed file isn't ready
4. **Network Timeouts**: File download/upload tests may take longer on slow connections

---

## Template Automation

### prepare_template_for_upload.py

This script automates Test 08 preparation by:
1. Downloading the template from S3 (generated in Test 07)
2. Loading the reference sample data from `utils/sample_boundary.xlsx`
3. Copying data rows (excluding headers) to the downloaded template
4. Saving the populated template as `output/sample_boundary.xlsx`

**Usage**:

```bash
# After Test 07 passes, run:
python3 prepare_template_for_upload.py

# Then run Test 08:
pytest tests/test_08_file_upload.py -v
```

**Script Flow**:

```
1. Get download URL from API (using Generated FileStore ID from ids.txt)
2. Download template from S3 → output/template_downloaded.xlsx
3. Load reference sample → utils/sample_boundary.xlsx
4. Extract headers from downloaded template (keep these - they match current hierarchy)
5. Copy data rows from sample (rows 2+)
6. Save populated template → output/sample_boundary.xlsx
7. Verify content and display summary
```

### Reference Sample File

**Location**: `utils/sample_boundary.xlsx`

**Important**: This file should NEVER be modified. It contains the reference boundary structure:
- 7 data rows representing the complete hierarchy
- Mozambique → Tete → Cahora Bassa → Chitima → Chibagadigo → CS de Chirodze Ponte → Chissua sedew
- Includes localization columns (French, Portuguese)
- Contains coordinate data (Latitude, Longitude)

---

## Reporting

### Test Logs

Test execution logs are stored in the `logs/` directory:

```bash
# View most recent log
cat logs/test_run_output.log

# Save test run to logs with timestamp
pytest tests/ -v -s > logs/test_run_$(date +%Y%m%d_%H%M%S).log 2>&1

# View logs with pagination
less logs/test_run_output.log

# View last 50 lines
tail -50 logs/test_run_output.log
```

See `logs/README.md` for detailed logging documentation.

### Output Files

1. **output/ids.txt**
   - Stores hierarchy type and generated IDs
   - Format:
     ```
     Hierarchy Type: TEST_D35387CC
     Generate ID: 7584fdcf-d7db-45a7-bc10-57256edd71ed
     Generated FileStore ID: c890d523-59e6-4ffd-a7a9-650fab42ec97
     Uploaded FileStore ID: 5bb7fecd-3cb2-44a9-a7cf-4b2ef5902781
     ```

2. **output/template_downloaded.xlsx**
   - Template downloaded from S3 in Test 07
   - Contains headers matching current hierarchy type
   - Initially empty (no data rows)

3. **output/sample_boundary.xlsx**
   - Populated template ready for upload in Test 08
   - Headers from downloaded template + data from reference sample

### Report Types

1. **HTML Report** (`reports/report.html`)
   ```bash
   pytest tests/ --html=reports/report.html --self-contained-html
   ```
   - Self-contained HTML file
   - Pass/Fail summary
   - Execution time
   - Error details with stack traces

2. **Allure Report**
   ```bash
   # Generate results
   pytest tests/ --alluredir=allure-results

   # Generate report
   allure generate allure-results --clean -o allure-report

   # Open in browser (Method 1 - using allure)
   allure open allure-report

   # Alternative Method 2 - if allure open fails (Java issues)
   # Start local HTTP server
   python3 -m http.server 8080 -d allure-report &
   # Open in browser
   xdg-open http://localhost:8080

   # Stop the server when done
   pkill -f "python3 -m http.server 8080"
   ```
   - Rich interactive web report
   - Test execution trends
   - Detailed logs and attachments
   - **Note**: Use Alternative Method 2 if you encounter Java symbol lookup errors with `allure open`

---

## Utilities Documentation

### api_client.py

HTTP client wrapper with automatic authentication.

```python
from utils.api_client import APIClient

# Initialize with token
client = APIClient(token="your_token")

# Make requests
response = client.get("/endpoint")
response = client.post("/endpoint", payload)
```

**Methods:**
- `get(endpoint)`: GET request
- `post(endpoint, data)`: POST request with JSON data

### auth.py

OAuth2 token management.

```python
from utils.auth import get_auth_token

token = get_auth_token("user")
```

### config.py

Environment variable loader.

```python
from utils.config import BASE_URL, tenantId

url = BASE_URL
tenant = tenantId
```

### data_loader.py

JSON payload loader.

```python
from utils.data_loader import load_payload

payload = load_payload("boundary_hierarchy", "create_hierarchy.json")
```

### request_info.py

RequestInfo object builder.

```python
from utils.request_info import get_request_info

payload["RequestInfo"] = get_request_info(token)
```

---

## Troubleshooting

### Common Issues

**1. Test 01 Fails: "INVALID_HIERARCHY_DEFINITION"**
- **Cause**: Case mismatch in boundary types
- **Solution**: Ensure all boundary types in `payloads/boundary_hierarchy/create_hierarchy.json` use UPPERCASE (COUNTRY, not Country)

**2. Test 08 Skipped: "Sample file not found"**
- **Cause**: `output/sample_boundary.xlsx` doesn't exist
- **Solution**: Run `prepare_template_for_upload.py` after Test 07 completes

**3. Test 09 Fails: "BOUNDARY_SHEET_HEADER_ERROR"**
- **Cause**: Template headers don't match hierarchy definition
- **Solution**:
  - Delete `output/template_downloaded.xlsx` and `output/sample_boundary.xlsx`
  - Re-run from Test 07 onwards
  - Ensure `prepare_template_for_upload.py` uses the correct template

**4. Authentication Failure**
- **Cause**: Invalid credentials or expired token
- **Solution**:
  - Verify `.env` credentials
  - Check `CLIENT_AUTH_HEADER` is properly base64 encoded
  - Test authentication: `python3 -c "from utils.auth import get_auth_token; print(get_auth_token('user'))"`

**5. Module Import Errors**
- **Cause**: Virtual environment not activated or missing dependencies
- **Solution**:
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

**6. File Upload Timeout**
- **Cause**: Large file or slow network
- **Solution**: Increase timeout in Test 08 or check network connection

### Debug Mode

Run tests with maximum verbosity:

```bash
pytest tests/ -vv -s --tb=long
```

**Flags:**
- `-vv`: Very verbose output
- `-s`: Show print statements
- `--tb=long`: Long traceback format

---

## Recent Fixes (2025-11-20)

### Fix: Boundary Hierarchy Case Mismatch

**Commit**: `7a76f47` - "Fix boundary hierarchy case mismatch and add template automation"

**Changes:**
1. Fixed `payloads/boundary_hierarchy/create_hierarchy.json`:
   - Changed `"Country"` → `"COUNTRY"`
   - Changed `parentBoundaryType: "Country"` → `"COUNTRY"`

2. Updated `tests/test_03_localization_upsert.py`:
   - Changed localization code from `f"{hierarchy_type}_Country"` → `f"{hierarchy_type}_COUNTRY"`

3. Added `prepare_template_for_upload.py` for template automation

4. Added `utils/sample_boundary.xlsx` as permanent reference file

**Result**: All 15 tests now pass (14 passed, 1 skipped)

---

## Best Practices

1. **Always run tests in sequence**: Tests 01-15 have dependencies
2. **Clear output directory** before fresh runs to avoid stale data
3. **Never modify** `utils/sample_boundary.xlsx` - it's the reference template
4. **Use prepare_template_for_upload.py** for Test 08 to ensure proper header matching
5. **NEVER commit the `.env` file** - it contains sensitive credentials and is excluded via `.gitignore`
6. **Create `.env` on each environment** - it's not in the repository, so you must create it manually
7. **Commit frequently** with meaningful messages
8. **Review output/ids.txt** after each test run to verify ID generation
9. **Check logs/** directory for detailed test execution logs

---

## Contributing

1. Create a feature branch: `git checkout -b feature/new-test`
2. Make changes with clear commit messages
3. Add tests for new functionality
4. Update documentation
5. Create pull request to `main` branch

---

## License

[Add license information here]

---

## Contact

- Repository: https://github.com/Shreya-egov/API_Automation
- Issues: https://github.com/Shreya-egov/API_Automation/issues

---

**Last Updated**: 2025-11-21
