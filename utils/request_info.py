import time
from utils.config import locale

def get_request_info(token: str) -> dict:
    # Generate timestamp|locale format for msgId
    timestamp = int(time.time() * 1000)
    msg_id = f"{timestamp}|{locale}"

    return {
        "apiId": "Rainmaker",
        "ver": "1.0",
        "ts": 0,
        "action": "create",
        "msgId": msg_id,
        "authToken": token,
        "userInfo": {
            "id": 16164561,
            "userName": "auto_user",
            "type": "EMPLOYEE",
            "uuid": "ac775061-7078-41b9-83bc-bfd1d064d20b",
            "tenantId": "mz",
            "roles": [
                {
                    "name": "District Supervisor",
                    "code": "DISTRICT_SUPERVISOR",
                    "tenantId": "mz"
                }
            ]
        },
        "plainAccessRequest": {}
    }
