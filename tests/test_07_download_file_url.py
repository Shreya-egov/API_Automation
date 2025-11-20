from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.config import tenantId
import allure
import json
import pytest


def download_file_url(token, client, file_store_id):
    """
    Helper function to get file download URL
    Returns: response object
    """
    # Make API call with query parameters
    url = f"/filestore/v1/files/url?tenantId={tenantId}&fileStoreIds={file_store_id}"
    response = client.get(url)

    return response


@pytest.mark.order(7)
@allure.feature("File Store")
@allure.story("Download File")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Test Get File Download URL")
@allure.description("Retrieves the download URL for a file stored in filestore")
def test_download_file_url():
    """Test getting download URL for a file"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the file store ID from file
    try:
        file_store_id = None

        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("FileStore ID:") or line.startswith("Uploaded FileStore ID:"):
                    file_store_id = line.split(":", 1)[1].strip()
                    break

        if not file_store_id:
            print("Skipping test: No FileStore ID found. Upload a file first.")
            return

        response = download_file_url(token, client, file_store_id)

        assert response.status_code == 200, f"File URL retrieval failed: {response.text}"

        data = response.json()
        file_store_ids = data.get("fileStoreIds", [])

        if len(file_store_ids) > 0:
            download_url = file_store_ids[0].get("url")
            print(f"Download URL retrieved successfully")
            print(f"URL: {download_url[:100]}..." if len(download_url) > 100 else f"URL: {download_url}")
        else:
            print("No file URLs found in response")

    except FileNotFoundError:
        print("No ids.txt file found. Run previous tests first.")
