# API Automation Framework

Comprehensive API automation testing framework for Boundary Management services using Python, Pytest, and Allure reporting.

![Tests](https://img.shields.io/badge/tests-14%20passed-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [Template Auto-Fill Feature](#template-auto-fill-feature-)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Allure Reports](#allure-reports)
- [Project Structure](#project-structure)
- [Test Coverage](#test-coverage)
- [Advanced Usage](#advanced-usage)
  - [Template Download and Auto-Fill](#template-download-and-auto-fill)
  - [Status Polling Configuration](#status-polling-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This framework automates testing for Boundary Management APIs including:
- Boundary Hierarchy Management
- Boundary Data Generation & Processing
- Boundary Relationships
- File Storage Operations
- Localization Services

**Key Highlights:**
- ✅ Intelligent status polling for async operations
- ✅ Comprehensive Allure reports with request/response attachments
- ✅ Modular and maintainable test structure
- ✅ Data-driven testing with JSON payloads
- ✅ Automatic test dependency management
- ✅ Template auto-fill with sample data for quick testing

## 🚀 Features

### Test Automation
- **Status Polling:** Automatically polls APIs until operations complete (configurable timeouts)
- **Smart Retries:** Configurable retry mechanism for async operations
- **Graceful Degradation:** Tests skip intelligently when dependencies are unavailable
- **Data Persistence:** Stores generated IDs and hierarchy types for test chaining

### Reporting
- **Allure Integration:** Rich, interactive HTML reports
- **Request/Response Capture:** Full API payload and response logging
- **Test Categorization:** Automatic failure classification
- **Historical Trends:** Track test execution over time
- **Screenshots & Attachments:** JSON payloads attached to each test

### Architecture
- **Modular Design:** Separate services for different API domains
- **Reusable Components:** Shared utilities for auth, config, and data loading
- **Environment Management:** Easy configuration switching
- **Clean Code:** Well-documented and maintainable

### Template Auto-Fill Feature ⭐
- **Automated Template Download:** Download boundary hierarchy templates via API
- **Smart Data Filling:** Automatically fills templates with sample boundary data
- **Code Replacement:** Intelligently replaces hierarchy type codes with current test data
- **Sample File Included:** Pre-configured sample file with multi-level boundary hierarchies
- **Seamless Integration:** Ready-to-upload files for testing

Learn more: [AUTO_FILL_FEATURE.md](AUTO_FILL_FEATURE.md)

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**
- **pip** (Python package manager)
- **Git**
- **Java 8+** (for Allure reporting)
- **Allure Command-line** (for report generation)

### Install Allure (Linux/Ubuntu)

```bash
# Install Java if not already installed
sudo apt-get update
sudo apt-get install openjdk-11-jdk -y

# Install Allure
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure -y

# Verify installation
allure --version
```

### Install Allure (macOS)

```bash
brew install allure
```

### Install Allure (Windows)

Download from: https://github.com/allure-framework/allure2/releases

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Shreya-egov/API_Automation.git
cd API_Automation
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Output Directory

```bash
mkdir -p output
```

## ⚙️ Configuration

### 1. Create Environment File

Create a `.env` file in the `utils/` directory with your configuration:

```bash
# API Configuration
BASE_URL=https://unified-qa.digit.org

# Authentication
USERNAME=SATYA
PASSWORD=eGov@1234
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic ZWdvdi11c2VyLWNsaWVudDo=

# Tenant Configuration
TENANTID=mz

# Search Parameters (Optional)
SEARCH_LIMIT=100
SEARCH_OFFSET=0

# Test Data (Optional)
HIERARCHYTYPE=
BOUNDARY_CODE=
BOUNDARY_TYPE=
```

**Note:** Update the `USERNAME` and `PASSWORD` with your actual credentials.

### 2. Verify Test Data

Test payloads are stored in `test_data/` directory. Review and update as needed:
- `boundary_hierarchy/` - Hierarchy creation and search payloads
- `boundary_management/` - Generation and processing payloads

## 🏃 Running Tests

### Quick Start (Automated Script)

**Linux/Mac:**
```bash
# Make script executable (first time only)
chmod +x run_tests.sh

# Run complete test suite
./run_tests.sh
```

**Windows:**
```cmd
run_tests.bat
```

The script automatically:
- Cleans previous results
- Runs all tests
- Generates Allure report
- Starts HTTP server
- Opens report in browser

### Quick Start (Manual)

```bash
# Run all tests with Allure results
pytest tests/ --alluredir=allure-results -v

# Generate and open report
allure generate allure-results --clean -o allure-report
allure open allure-report
```

**💡 For complete command reference, see [COMMANDS.md](COMMANDS.md)**

### Basic Commands

#### Run All Tests
```bash
pytest tests/ --alluredir=allure-results -v
```

#### Run Specific Test Suite
```bash
# Boundary Hierarchy tests
pytest tests/test_boundary_hierarchy_service.py --alluredir=allure-results -v

# Boundary Management tests
pytest tests/test_boundary_management_service.py --alluredir=allure-results -v

# Filestore tests
pytest tests/test_filestore_service.py --alluredir=allure-results -v

# Localization tests
pytest tests/test_localization_service.py --alluredir=allure-results -v
```

#### Run Specific Test
```bash
pytest tests/test_boundary_management_service.py::test_generate_boundary_data --alluredir=allure-results -v
```

#### Run with Clean Results (Fresh Start)
```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v
```

### Advanced Options

#### Verbose Output with Print Statements
```bash
pytest tests/ --alluredir=allure-results -v -s
```

#### Stop on First Failure
```bash
pytest tests/ --alluredir=allure-results -v -x
```

#### Run Tests in Parallel (requires pytest-xdist)
```bash
pytest tests/ --alluredir=allure-results -v -n 4
```

#### Show Test Execution Time
```bash
pytest tests/ --alluredir=allure-results -v --durations=10
```

## 📊 Allure Reports

### Generate and View Reports

#### Method 1: Using Python HTTP Server (Recommended)

This method is the most reliable and works across all environments:

```bash
# Step 1: Generate report
allure generate allure-results --clean -o allure-report

# Step 2: Start HTTP server (choose a port)
cd allure-report
python3 -m http.server 8080

# Step 3: Open browser to http://localhost:8080
```

**Note:** The server runs in the background. To stop it, press `Ctrl+C` or use:
```bash
pkill -f "python3 -m http.server 8080"
```

#### Method 2: One-Liner (Complete Flow)

Run tests and serve report in one command:

```bash
pytest tests/ --alluredir=allure-results --clean-alluredir -v && \
allure generate allure-results --clean -o allure-report && \
cd allure-report && python3 -m http.server 8080
```

Then open: **http://localhost:8080**

#### Method 3: Using Allure Server (Alternative)

```bash
# Generate and open report (may not work on all systems)
allure generate allure-results --clean -o allure-report
allure open allure-report
```

**Note:** If `allure serve` or `allure open` fails with Java errors, use Method 1 (Python HTTP Server) instead.

### Report Features

The Allure report includes:

- **Overview Dashboard** - Test execution summary and statistics
- **Suites** - Tests organized by test files
- **Graphs** - Visual representation of results
- **Timeline** - Test execution timeline
- **Behaviors** - Tests grouped by features and stories
- **Categories** - Automatic failure classification
- **Attachments** - Request/response payloads for every API call
- **Polling Progress** - Status updates for async operations

### Viewing Test Details

Click on any test in the report to see:
- ✅ Test status and duration
- 📄 Request payload (JSON formatted)
- 📄 Response status code
- 📄 Complete response body
- 🔄 Polling attempts (for async operations)
- 📊 Execution steps and logs

## 📁 Project Structure

```
API_Automation/
├── tests/                                      # Test files
│   ├── test_boundary_hierarchy_service.py     # Hierarchy creation and search
│   ├── test_boundary_management_service.py    # Data generation and processing
│   ├── test_boundary_relationships_service.py # Relationship queries
│   ├── test_filestore_service.py             # File upload/download
│   └── test_localization_service.py          # Localization operations
│
├── utils/                                     # Utility modules
│   ├── api_client.py                         # HTTP client wrapper
│   ├── auth.py                               # Authentication management
│   ├── config.py                             # Configuration settings
│   ├── data_loader.py                        # JSON payload loader
│   └── request_info.py                       # Request metadata builder
│
├── test_data/                                # Test data and payloads
│   ├── boundary_hierarchy/                   # Hierarchy test data
│   │   ├── create_hierarchy.json
│   │   └── search_hierarchy.json
│   ├── boundary_management/                  # Management test data
│   │   ├── generate_data.json
│   │   ├── generate_search.json
│   │   ├── process_data.json
│   │   └── process_search.json
│   └── ...
│
├── sample/                                   # Sample data files
│   └── sample.xlsx                          # Sample boundary data for auto-fill
│
├── output/                                   # Test execution output
│   ├── ids.txt                              # Generated IDs and hierarchy types
│   └── hierarchy_template_*_filled.xlsx     # Auto-filled templates
│
├── allure-results/                          # Allure test results (generated)
├── allure-report/                           # Allure HTML report (generated)
│
├── categories.json                          # Allure failure categories
├── pytest.ini                               # Pytest configuration
├── requirements.txt                         # Python dependencies
├── README.md                                # This file
├── COMMANDS.md                              # Quick command reference
├── run_tests.sh                             # Test execution script (Linux/Mac)
├── run_tests.bat                            # Test execution script (Windows)
├── download_hierarchy_template.py           # Template download utility
└── AUTO_FILL_FEATURE.md                     # Auto-fill feature documentation
```

## 🧪 Test Coverage

### 1. Boundary Hierarchy Service (2 tests)
- ✅ Create boundary hierarchy with unique type
- ✅ Search for created hierarchy

### 2. Boundary Management Service (4 tests)
- ✅ Generate boundary data (triggers async operation)
- ✅ Search generated boundary (polls until status = 'completed')
- ✅ Process boundary data from template
- ✅ Search processed boundary (polls until status = 'completed')

### 3. Boundary Relationships Service (2 tests)
- ✅ Search boundary relationships with children
- ✅ Search boundary relationships without children

### 4. Filestore Service (2 tests)
- ✅ Upload file to filestore
- ✅ Get download URL for uploaded file

### 5. Localization Service (4 tests)
- ✅ Upsert localization data
- ✅ Search localization (English)
- ✅ Search localization (French)
- ✅ Search localization (Portuguese)

**Total: 14 automated test scenarios**

## 🔬 Advanced Usage

### Template Download and Auto-Fill

The framework includes a powerful template download and auto-fill utility:

```bash
# Download template and auto-fill with sample data
python3 download_hierarchy_template.py
```

**What it does:**
1. Downloads the boundary hierarchy template from the API
2. Automatically fills it with data from `sample/sample.xlsx`
3. Replaces hierarchy type codes (e.g., TETE5_) with your current test hierarchy type
4. Saves a ready-to-upload filled template in `output/`

**Sample Data Included:**
- Multi-level hierarchies (Country → Province → District → Villages)
- Post Administrative levels and Health Facilities
- Service Boundary Codes
- Multi-language support (English, French, Portuguese)
- Latitude/Longitude coordinates

**Output Files:**
- `output/hierarchy_template_{TYPE}.xlsx` - Original template
- `output/hierarchy_template_{TYPE}_filled.xlsx` - Auto-filled and ready to use

For complete details, see [AUTO_FILL_FEATURE.md](AUTO_FILL_FEATURE.md)

### Status Polling Configuration

The framework automatically polls async APIs until completion. You can configure:

```python
# In test files
response = search_generated_boundary(
    token,
    client,
    hierarchy_type,
    wait_for_completion=True,  # Enable polling
    max_retries=30,            # Number of attempts
    retry_interval=5           # Seconds between attempts
)
```

### Accessing Generated Data

```bash
# View all generated data
cat output/ids.txt

# Get latest hierarchy type
grep "Hierarchy Type:" output/ids.txt | tail -1

# Get all resource IDs
grep "Generate Resource ID:" output/ids.txt
```

### Custom Test Data

To add new test scenarios:

1. Create JSON payload in `test_data/`
2. Load in test using `load_payload()`
3. Add test function with Allure decorators

Example:
```python
@allure.feature("Your Feature")
@allure.story("Your Story")
@allure.severity(allure.severity_level.CRITICAL)
def test_your_scenario():
    payload = load_payload("your_folder", "your_file.json")
    # Your test code
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Failures
```bash
Error: 401 Unauthorized
Solution: Update credentials in utils/auth.py
```

#### 2. Connection Errors
```bash
Error: Connection refused
Solution: Verify BASE_URL in utils/config.py and network connectivity
```

#### 3. Allure Report 404 Error
```bash
Solution: Use HTTP server instead of opening file directly
cd allure-report && python3 -m http.server 8000
```

#### 4. Tests Hanging
```bash
Issue: Tests waiting indefinitely
Solution: Check max_retries and retry_interval in polling functions
```

#### 5. Import Errors
```bash
Error: ModuleNotFoundError
Solution: Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

### Debug Mode

Run tests with verbose output and print statements:
```bash
pytest tests/ --alluredir=allure-results -v -s --log-cli-level=DEBUG
```

### Clean Up

```bash
# Remove generated files
rm -rf allure-results/ allure-report/ output/ids.txt

# Stop HTTP server
pkill -f "python3 -m http.server 8000"
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit changes: `git commit -m "Add your feature"`
6. Push to branch: `git push origin feature/your-feature`
7. Create a Pull Request

### Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include Allure decorators for new tests
- Update README for new features
- Attach request/response data in tests

### Test Naming Convention

```python
# Format: test_<action>_<entity>
def test_create_boundary_hierarchy():
def test_search_generated_boundary():
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Shreya Kumar** - [Shreya-egov](https://github.com/Shreya-egov)

## 🙏 Acknowledgments

- Built with [Pytest](https://pytest.org/)
- Reporting powered by [Allure Framework](https://docs.qameta.io/allure/)
- API testing with [Requests](https://requests.readthedocs.io/)

## 📞 Support

For issues and questions:
- Create an issue on [GitHub](https://github.com/Shreya-egov/API_Automation/issues)
- Contact: shreya.kumar@egovernments.org

---

**Happy Testing! 🚀**

*Last Updated: November 13, 2025*
