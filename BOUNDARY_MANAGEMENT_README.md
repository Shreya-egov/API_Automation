# Boundary Management API Automation Framework

## Overview

This is a comprehensive API automation framework for testing **Boundary Management services** in the DIGIT platform. The framework is built using **Python 3.12** and **Pytest**, following the same architectural patterns as the existing HCM services automation.

## Services Covered

### 1. Boundary Hierarchy Service
- **Create Boundary Hierarchy** - Define hierarchical boundary structures
- **Search Boundary Hierarchy** - Query existing boundary definitions

### 2. Localization Service
- **Upsert Localization** - Create/update localization messages
- **Search Localization** - Query messages in multiple locales (English, French, Portuguese)

### 3. Boundary Management Service
- **Generate Boundary Data** - Trigger boundary data generation
- **Search Generated Data** - Query generation status and results
- **Process Boundary Data** - Process uploaded boundary files
- **Search Processed Data** - Query processing status and results

### 4. Filestore Service
- **Upload Files** - Upload boundary data files (Excel/CSV)
- **Download File URLs** - Retrieve download URLs for stored files

### 5. Boundary Relationships Service
- **Search Relationships** - Query boundary hierarchies with parent-child relationships

---

## Directory Structure

```
API_Automation/
├── tests/
│   ├── test_boundary_hierarchy_service.py      # Hierarchy create/search tests
│   ├── test_localization_service.py            # Localization upsert/search tests
│   ├── test_boundary_management_service.py     # Generate/process tests
│   ├── test_filestore_service.py               # File upload/download tests
│   └── test_boundary_relationships_service.py  # Relationship search tests
├── payloads/
│   ├── boundary_hierarchy/
│   │   ├── create_hierarchy.json
│   │   └── search_hierarchy.json
│   ├── localization/
│   │   ├── upsert_localization.json
│   │   └── search_localization.json
│   ├── boundary_management/
│   │   ├── generate_data.json
│   │   ├── generate_search.json
│   │   ├── process_data.json
│   │   └── process_search.json
│   ├── filestore/                              # (File uploads use multipart)
│   └── boundary_relationships/
│       └── search_relationships.json
├── utils/
│   ├── auth.py                                 # OAuth2 authentication
│   ├── api_client.py                           # HTTP client wrapper
│   ├── config.py                               # Configuration management
│   ├── data_loader.py                          # Payload loader
│   ├── request_info.py                         # RequestInfo builder
│   └── search_helpers.py                       # Search utilities
├── output/
│   ├── ids.txt                                 # Generated entity IDs
│   ├── response.json                           # Latest API response
│   └── boundary_relationships.json             # Boundary hierarchy data
├── reports/
│   └── report.html                             # Pytest HTML reports
├── utils/.env                                  # Environment variables
├── pytest.ini                                  # Pytest configuration
└── requirements.txt                            # Python dependencies
```

---

## Test Execution Flow

### 1. Boundary Hierarchy Tests

#### Create Hierarchy
```bash
pytest tests/test_boundary_hierarchy_service.py::test_create_boundary_hierarchy -v
```
- Generates unique hierarchy type (e.g., `TEST_ABC123`)
- Creates boundary hierarchy with 7 levels:
  - Country → Province → District → Post Administrative → Locality → Health Facility → Village
- Stores hierarchy type in `output/ids.txt`

#### Search Hierarchy
```bash
pytest tests/test_boundary_hierarchy_service.py::test_search_boundary_hierarchy -v
```
- Searches for created hierarchy
- Validates boundary structure
- Displays hierarchy configuration

### 2. Localization Tests

#### Upsert Localization
```bash
pytest tests/test_localization_service.py::test_upsert_localization -v
```
- Creates localization messages for hierarchy types
- Supports multiple boundary levels
- Uses hierarchy type from previous tests

#### Search Localization (Multiple Locales)
```bash
# English
pytest tests/test_localization_service.py::test_search_localization_english -v

# French
pytest tests/test_localization_service.py::test_search_localization_french -v

# Portuguese
pytest tests/test_localization_service.py::test_search_localization_portuguese -v
```
- Queries messages in different locales
- Validates message codes and content

### 3. Boundary Management Tests

#### Generate Boundary Data
```bash
pytest tests/test_boundary_management_service.py::test_generate_boundary_data -v
```
- Triggers boundary data generation
- Stores resource ID for tracking

#### Search Generated Data
```bash
pytest tests/test_boundary_management_service.py::test_search_generated_boundary -v
```
- Checks generation status
- Retrieves fileStore ID for generated data
- Waits for generation completion

#### Process Boundary Data
```bash
pytest tests/test_boundary_management_service.py::test_process_boundary_data -v
```
- Processes uploaded boundary file
- Requires fileStoreId from file upload
- Stores process ID

#### Search Processed Data
```bash
pytest tests/test_boundary_management_service.py::test_search_processed_boundary -v
```
- Checks processing status
- Retrieves processed file details

### 4. Filestore Tests

#### Upload File
```bash
pytest tests/test_filestore_service.py::test_upload_file -v
```
- Uploads boundary data file (Excel/CSV)
- Stores fileStore ID
- **Note:** Update file path in test before running

#### Download File URL
```bash
pytest tests/test_filestore_service.py::test_download_file_url -v
```
- Retrieves download URL for stored file
- Displays URL for verification

### 5. Boundary Relationships Tests

#### Search Relationships
```bash
# With children
pytest tests/test_boundary_relationships_service.py::test_search_boundary_relationships -v

# Without children
pytest tests/test_boundary_relationships_service.py::test_search_boundary_relationships_without_children -v
```
- Queries complete boundary hierarchy
- Saves relationship data to JSON
- Displays hierarchy structure

---

## Running Tests

### Run All Boundary Management Tests
```bash
pytest tests/test_boundary_hierarchy_service.py tests/test_localization_service.py tests/test_boundary_management_service.py tests/test_filestore_service.py tests/test_boundary_relationships_service.py -v
```

### Run Specific Service Tests
```bash
# Hierarchy tests only
pytest tests/test_boundary_hierarchy_service.py -v

# Localization tests only
pytest tests/test_localization_service.py -v

# Management tests only
pytest tests/test_boundary_management_service.py -v
```

### Generate HTML Report
```bash
pytest tests/test_boundary_*.py tests/test_localization_service.py tests/test_filestore_service.py -v --html=reports/boundary_report.html --self-contained-html
```

### Run with Output Capture
```bash
pytest tests/test_boundary_*.py tests/test_localization_service.py -v -s
```

---

## Configuration

### Environment Variables (`utils/.env`)

```bash
# API Configuration
BASE_URL=https://health-demo.digit.org
TENANTID=mz

# Authentication
USERNAME=SATYA
PASSWORD=eGov@1234
USERTYPE=EMPLOYEE
CLIENT_AUTH_HEADER=Basic ZWdvdi11c2VyLWNsaWVudDo=

# Search Parameters
SEARCH_LIMIT=200
SEARCH_OFFSET=0

# Service Names
SERVICE_INDIVIDUAL=individual
SERVICE_PROJECT=project
SERVICE_MDMS=mdms-v2
```

---

## Key Features

### 1. **Dynamic Data Injection**
- Unique hierarchy types generated per test run
- Automatic UUID generation for entities
- RequestInfo built dynamically

### 2. **ID Persistence**
- All generated IDs stored in `output/ids.txt`
- Cross-test dependencies managed via file
- Easy tracking of created resources

### 3. **Multi-Locale Support**
- Test localization in English, French, Portuguese
- Locale-specific message validation
- Module naming conventions

### 4. **File Operations**
- Upload Excel/CSV boundary files
- Retrieve download URLs
- Process uploaded data

### 5. **Relationship Mapping**
- Complete hierarchy traversal
- Parent-child relationship validation
- JSON export of boundary structure

---

## Test Dependencies

### Test Execution Order (Recommended)

1. **Boundary Hierarchy Create** - Creates hierarchy type
2. **Boundary Hierarchy Search** - Validates creation
3. **Localization Upsert** - Creates messages for hierarchy
4. **Localization Search** - Validates messages
5. **Boundary Management Generate** - Triggers generation
6. **Boundary Management Search** - Checks generation status
7. **Filestore Upload** - Uploads boundary file (optional)
8. **Boundary Management Process** - Processes uploaded file (requires upload)
9. **Boundary Management Process Search** - Checks processing status
10. **Boundary Relationships Search** - Validates complete hierarchy

---

## Common Issues & Solutions

### 1. **SSL Certificate Error**
- **Issue:** `SSLError: certificate verify failed`
- **Solution:** Already fixed - `verify=False` in `utils/auth.py` and `utils/api_client.py`

### 2. **FileStore ID Not Found**
- **Issue:** Process tests fail with "No FileStore ID found"
- **Solution:** Run file upload test first or use generated fileStore ID from generate-search

### 3. **Hierarchy Type Not Found**
- **Issue:** Tests fail with "Hierarchy Type not found in ids.txt"
- **Solution:** Run boundary hierarchy create test first

### 4. **File Upload Path Error**
- **Issue:** File upload test skipped
- **Solution:** Update `test_file_path` in `test_filestore_service.py:test_upload_file()` with valid file path

### 5. **Empty Localization Results**
- **Issue:** Search returns empty messages
- **Solution:** Run upsert test first, ensure hierarchy type exists

---

## API Endpoints

| Service | Method | Endpoint | Description |
|---------|--------|----------|-------------|
| **Boundary Hierarchy** | POST | `/boundary-service/boundary-hierarchy-definition/_create` | Create hierarchy |
| **Boundary Hierarchy** | POST | `/boundary-service/boundary-hierarchy-definition/_search` | Search hierarchy |
| **Localization** | POST | `/localization/messages/v1/_upsert` | Upsert messages |
| **Localization** | POST | `/localization/messages/v1/_search` | Search messages |
| **Boundary Management** | POST | `/boundary-management/v1/_generate` | Generate data |
| **Boundary Management** | POST | `/boundary-management/v1/_generate-search` | Search generation |
| **Boundary Management** | POST | `/boundary-management/v1/_process` | Process data |
| **Boundary Management** | POST | `/boundary-management/v1/_process-search` | Search processing |
| **Filestore** | POST | `/filestore/v1/files` | Upload file |
| **Filestore** | GET | `/filestore/v1/files/url` | Get download URL |
| **Boundary Relationships** | POST | `/boundary-service/boundary-relationships/_search` | Search relationships |

---

## Output Files

### `output/ids.txt`
Stores all generated IDs:
```
Hierarchy Type: TEST_ABC12345
Generate Resource ID: res-123-456
FileStore ID: fs-789-012
Process ID: proc-345-678
```

### `output/boundary_relationships.json`
Complete boundary hierarchy structure with parent-child relationships.

### `reports/report.html`
Pytest HTML report with:
- Test execution summary
- Pass/fail status
- Execution time
- Error details

---

## Next Steps

1. **Update File Path** - Modify file path in `test_filestore_service.py` for upload tests
2. **Run Tests** - Execute in recommended order
3. **Verify Results** - Check `output/ids.txt` and reports
4. **Customize Payloads** - Modify JSON templates in `payloads/` as needed
5. **Add Assertions** - Enhance test validations based on requirements

---

## Support

For issues or questions:
1. Check `output/ids.txt` for generated IDs
2. Review `reports/report.html` for detailed test results
3. Examine API responses in `output/response.json`
4. Verify environment configuration in `utils/.env`

---

**Created:** 2025-01-13
**Framework Version:** 1.0
**Python Version:** 3.12+
**Pytest Version:** 9.0.0
