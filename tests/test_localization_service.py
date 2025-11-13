from utils.api_client import APIClient
from utils.auth import get_auth_token
from utils.data_loader import load_payload
from utils.request_info import get_request_info
from utils.config import tenantId
import os
import allure
import json


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


def search_localization(token, client, hierarchy_type, locale="en_MZ"):
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


def test_search_localization_english():
    """Test searching localization messages in English"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_localization(token, client, hierarchy_type, locale="en_MZ")

        assert response.status_code == 200, f"Localization search failed: {response.text}"

        data = response.json()
        messages = data.get("messages", [])

        assert len(messages) > 0, "No localization messages found"

        print(f"Found {len(messages)} localization messages")
        print(f"Sample message: {messages[0].get('code')} - {messages[0].get('message')}")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"


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


def test_search_localization_portuguese():
    """Test searching localization messages in Portuguese"""
    token = get_auth_token("user")
    client = APIClient(token=token)

    # Read the hierarchy type from file
    try:
        with open("output/ids.txt", "r") as f:
            for line in f:
                if line.startswith("Hierarchy Type:"):
                    hierarchy_type = line.split(":")[1].strip()
                    break

        response = search_localization(token, client, hierarchy_type, locale="pt_MZ")

        assert response.status_code == 200, f"Localization search failed: {response.text}"

        data = response.json()
        messages = data.get("messages", [])

        print(f"Found {len(messages)} Portuguese localization messages")
        if len(messages) > 0:
            print(f"Sample message: {messages[0].get('code')} - {messages[0].get('message')}")

    except FileNotFoundError:
        print("No hierarchy type found. Run boundary hierarchy create test first.")
        assert False, "Hierarchy Type not found in ids.txt"
