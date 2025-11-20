from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import allure
import json
import pytest


def search_localization(token, client, hierarchy_type, locale="fr_MZ"):
    """
    Helper function to search localization messages
    Returns: response object
    """
    payload = load_payload("localization", "search_localization.json")

    # Get hierarchy type in lowercase for module naming
    hierarchy_type_lower = hierarchy_type.lower()

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)

    # Make API call with query parameters
    url = f"/localization/messages/v1/_search?tenantId={tenantId}&locale={locale}&module=hcm-boundary-{hierarchy_type_lower}"
    response = client.post(url, payload)

    return response


@pytest.mark.order(11)
@allure.feature("Localization")
@allure.story("Search Localization")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Test Search Localization Messages - French")
@allure.description("Searches for localization messages in French locale (fr_MZ)")
def test_search_localization_french():
    """Test searching localization messages in French"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_localization(token, client, hierarchy_type, locale="fr_MZ")

        assert response.status_code == 200, f"Localization search failed: {response.text}"

        data = response.json()
        messages = data.get("messages", [])

        print(f"Found {len(messages)} French localization messages")
        if len(messages) > 0:
            print(f"Sample message: {messages[0].get('code')} - {messages[0].get('message')}")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
