import os
import requests
from dotenv import load_dotenv
from utils.config import tenantId
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv(override=True)  # This forces reloading of updated values

def get_auth_token(service: str):
    url = os.getenv("BASE_URL") + "/user/oauth/token"
    # print("URL ", url)

    # Build dynamic payload based on service (role)
    payload = {
        "username": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "grant_type": "password",
        "scope": "read",
        "tenantId": tenantId,
        "userType": os.getenv("USERTYPE")
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": os.getenv("CLIENT_AUTH_HEADER"),
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers, verify=False)
    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json().get("access_token")
