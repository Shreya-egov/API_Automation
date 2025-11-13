from utils.auth import get_auth_token
from utils.config import BASE_URL
from utils.logger import setup_logger
import requests
import urllib3
import json

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logger
logger = setup_logger(__name__)

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
        url = BASE_URL + endpoint
        logger.info(f"GET Request: {url}")
        response = requests.get(url, headers=self.headers, verify=False)
        logger.info(f"GET Response: Status {response.status_code}")
        logger.debug(f"Response: {response.text[:500]}")
        return response

    def post(self, endpoint, data):
        url = BASE_URL + endpoint
        logger.info(f"POST Request: {url}")
        logger.debug(f"Request Payload: {json.dumps(data, indent=2)[:1000]}")
        response = requests.post(url, headers=self.headers, json=data, verify=False)
        logger.info(f"POST Response: Status {response.status_code}")
        logger.debug(f"Response: {response.text[:500]}")
        return response

    def put(self, endpoint, data):
        url = BASE_URL + endpoint
        logger.info(f"PUT Request: {url}")
        logger.debug(f"Request Payload: {json.dumps(data, indent=2)[:1000]}")
        response = requests.put(url, headers=self.headers, json=data, verify=False)
        logger.info(f"PUT Response: Status {response.status_code}")
        logger.debug(f"Response: {response.text[:500]}")
        return response

    def delete(self, endpoint):
        url = BASE_URL + endpoint
        logger.info(f"DELETE Request: {url}")
        response = requests.delete(url, headers=self.headers, verify=False)
        logger.info(f"DELETE Response: Status {response.status_code}")
        logger.debug(f"Response: {response.text[:500]}")
        return response