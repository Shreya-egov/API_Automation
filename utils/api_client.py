from utils.auth import get_auth_token
from utils.config import BASE_URL
import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIClient:
    def __init__(self, service=None, token=None):
        if not token and service:
            token = get_auth_token(service)
        elif not token:
            raise ValueError("Either 'service' or 'token' must be provided")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def get(self, endpoint):
        return requests.get(BASE_URL + endpoint, headers=self.headers, verify=False)

    def post(self, endpoint, data):
        return requests.post(BASE_URL + endpoint, headers=self.headers, json=data, verify=False)

    def put(self, endpoint, data):
        return requests.put(BASE_URL + endpoint, headers=self.headers, json=data, verify=False)

    def delete(self, endpoint):
        return requests.delete(BASE_URL + endpoint, headers=self.headers, verify=False)