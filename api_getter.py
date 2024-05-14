import requests
import json
import uuid
from dotenv import load_dotenv
import os


def api_getter():

    url = os.environ.get('ENV_GIGACHAT_URL') 

    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': 'Basic '+ os.environ.get('ENV_GIGACHAT_TOKEN'),
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    token_data = json.loads(response.text)
    access_token = token_data["access_token"]
    expires_at = token_data["expires_at"]
    print(token_data)

    return token_data

