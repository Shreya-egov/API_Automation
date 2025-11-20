from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId, BASE_URL
import pytest
import requests
import os


@pytest.mark.order(8)
def test_file_upload():
    """Test uploading a file"""
    token = get_auth_token("user")

    # For now, skip if no sample file exists
    # In real scenario, you would download and fill the template first
    sample_file = "output/sample_boundary.xlsx"

    if not os.path.exists(sample_file):
        pytest.skip("Sample file not found. Download and fill template first.")

    # Prepare multipart form data
    files = {
        'file': (os.path.basename(sample_file), open(sample_file, 'rb'),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data = {
        'tenantId': tenantId,
        'module': 'HCM-ADMIN-CONSOLE'
    }

    # Make direct request
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/filestore/v1/files",
        files=files,
        data=data,
        headers=headers,
        verify=False
    )

    files['file'][1].close()

    assert response.status_code in [200, 201], f"File upload failed: {response.text}"

    data = response.json()
    file_store_id = data["files"][0]["fileStoreId"]

    print(f"File uploaded successfully: {file_store_id}")

    # Save file store ID
    with open("output/ids.txt", "a") as f:
        f.write(f"Uploaded FileStore ID: {file_store_id}\n")
