from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import os
import allure
import json
import pytest


def upsert_localization(token, client, hierarchy_type, locale="en_MZ"):
    """
    Helper function to upsert localization messages
    Returns: response object
    """
    payload = load_payload("localization", "upsert_localization.json")

    # Get hierarchy type in lowercase for module naming
    hierarchy_type_lower = hierarchy_type.lower()

    # Inject dynamic data
    payload["RequestInfo"] = get_request_info(token)
    payload["tenantId"] = tenantId
    payload["messages"] = [
        {
            "code": f"{hierarchy_type}_COUNTRY",
            "message": "Country",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_PROVINCE",
            "message": "Province",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_DISTRICT",
            "message": "Distrito",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_POST ADMINISTRATIVE",
            "message": "Post administrative",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_LOCALITY",
            "message": "Locality",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_HEALTH FACILITY",
            "message": "Health Facility",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        },
        {
            "code": f"{hierarchy_type}_VILLAGE",
            "message": "Village",
            "module": f"hcm-boundary-{hierarchy_type_lower}",
            "locale": locale
        }
    ]

    # Make API call
    response = client.post("/localization/messages/v1/_upsert", payload)

    return response


@pytest.mark.order(3)
@allure.feature("Localization")
@allure.story("Upsert Localization")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Test Upsert Localization Messages")
@allure.description("Creates or updates localization messages for boundary hierarchy types")
def test_upsert_localization():
    """Test upserting localization messages"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = upsert_localization(token, client, hierarchy_type)

        assert response.status_code in [200, 201], f"Localization upsert failed: {response.text}"

        data = response.json()
        messages_count = data.get("messages", [])

        print(f"Localization messages upserted: {len(messages_count)} messages")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
