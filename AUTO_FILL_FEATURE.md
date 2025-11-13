# Auto-Fill Template Feature

## Overview
The `download_hierarchy_template.py` script has been enhanced to automatically fill downloaded boundary templates with sample data.

## What's New

### Automatic Template Filling
After downloading the boundary hierarchy template, the script now:

1. **Downloads the template** from the Boundary Management API
2. **Automatically fills it** with data from a sample file
3. **Replaces hierarchy type codes** with the current hierarchy type
4. **Saves the filled template** ready for upload

## How It Works

### Step-by-Step Process

1. **Authentication** - Gets auth token
2. **Generate Template** - Triggers template generation
3. **Wait for Generation** - Polls until template is ready
4. **Download Template** - Retrieves the generated template
5. **Get Download URL** - Gets the file download link
6. **Auto-Fill** ⭐ NEW - Fills template with sample data

### Auto-Fill Logic

```python
def fill_template_with_sample(template_file, hierarchy_type, sample_file):
    """
    Fills the downloaded template with data from sample file
    - Extracts sample Excel file
    - Replaces old hierarchy type codes (e.g., TETE5) with new type
    - Updates both shared strings and worksheet data
    - Creates filled Excel file
    """
```

## Sample File Location

**Default Sample File:** `sample/sample.xlsx` (in the repository)

The script automatically looks for this file. If not found, it skips auto-fill and you can manually fill the template.

## Usage

### Run the Script

```bash
cd /home/shreya-kumar/Desktop/API\ Automation/API_Automation
python3 download_hierarchy_template.py
```

### Output Files

1. **Original Template:** `output/hierarchy_template_{HIERARCHY_TYPE}.xlsx`
2. **Filled Template:** `output/hierarchy_template_{HIERARCHY_TYPE}_filled.xlsx` ⭐

### Example Output

```
================================================================================
HIERARCHY TEMPLATE DOWNLOAD WORKFLOW
================================================================================

Step 1: Authenticating...
✓ Authentication successful

Step 2: Generating template for hierarchy: TEST_69089BE7
✓ Template generation triggered
  Resource ID: 0a4e033b-a81b-4f53-81ed-d1740d7edc4f

Step 3: Waiting for template generation...
✓ Template generated successfully!
  FileStore ID: 661b7220-a681-42d9-980b-01e336be21e0

Step 4: Retrieving download URL...
✓ Download URL retrieved

Step 5: Downloading template file...
✓ Template downloaded successfully!
  File saved to: output/hierarchy_template_TEST_69089BE7.xlsx
  File size: 127464 bytes

Step 6: Auto-filling template with sample data...
  ✓ Extracted sample file
  ✓ Updated localization strings with hierarchy type: TEST_69089BE7
  ✓ Updated worksheet data
✓ Template auto-filled successfully!
  Filled file: output/hierarchy_template_TEST_69089BE7_filled.xlsx
  Sample file used: sample/sample.xlsx

================================================================================
NEXT STEPS:
================================================================================
1. Review the filled file: output/hierarchy_template_TEST_69089BE7_filled.xlsx
2. Modify boundary data if needed (codes, names, coordinates, etc.)
3. Upload using test_upload_file test
4. Process using test_process_boundary_data test

================================================================================
SUCCESS! Filled template ready at: output/hierarchy_template_TEST_69089BE7_filled.xlsx
================================================================================
The template has been auto-filled with sample data.
Hierarchy type codes updated to: TEST_69089BE7
Ready for upload and processing!
================================================================================
```

## Features

### Smart Code Replacement

The script uses regex pattern matching to replace hierarchy type codes:

- **Pattern:** `[A-Z]+\d+_` (e.g., TETE5_, DEMO123_)
- **Replacement:** `{hierarchy_type}_` (e.g., TEST_69089BE7_)

### Examples:

| Original Code | Replaced Code |
|--------------|---------------|
| `TETE5_COUNTRY` | `TEST_69089BE7_COUNTRY` |
| `TETE5_MO_01_TETE` | `TEST_69089BE7_MO_01_TETE` |
| `TETE5_PROVINCE` | `TEST_69089BE7_PROVINCE` |

### Data Preservation

All boundary data from the sample file is preserved:
- Country, Province, District hierarchies
- Post Administrative, Locality levels
- Health Facilities and Villages
- Service Boundary Codes
- French and Portuguese translations
- Latitude and Longitude coordinates

## Error Handling

If the sample file is not found:
```
⚠ Sample file not found at: sample/sample.xlsx
⚠ Skipping auto-fill. You can manually fill the template.
```

The script continues and returns the original template file.

## Configuration

To use a different sample file, modify the default parameter:

```python
def fill_template_with_sample(
    template_file,
    hierarchy_type,
    sample_file="sample/sample.xlsx"  # Change this path if needed
):
```

Or call the function directly with a custom path in your tests.

## Benefits

✅ **Time Saving** - No manual data entry required
✅ **Consistency** - Automatic code replacement ensures consistency
✅ **Error Reduction** - Less manual work = fewer errors
✅ **Seamless Integration** - Works with existing workflow
✅ **Flexible** - Falls back gracefully if sample not available

## Next Steps After Auto-Fill

1. **Review** the filled file
2. **Modify** if needed (add more boundaries, update coordinates)
3. **Upload** using File Upload API
4. **Process** using Process Data API
5. **Verify** using Process Search API

## File Structure

```
output/
├── hierarchy_template_TEST_69089BE7.xlsx        # Original template
├── hierarchy_template_TEST_69089BE7_filled.xlsx # Auto-filled template ⭐
├── template_download_url.txt                    # Download URL
└── ids.txt                                      # Resource IDs
```

## Integration with Tests

The filled file is now ready to use in your test suite:

```python
def test_upload_file():
    # Use the auto-filled file
    file_path = "output/hierarchy_template_TEST_69089BE7_filled.xlsx"
    file_store_id, status = upload_file(token, client, file_path)
    # Continue with processing...
```

---

**Created:** 2025-11-12
**Author:** Claude Code Automation Framework
**Version:** 1.0
