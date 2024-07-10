import msal
import requests
import json

tenant_id = '41e9b618-6728-42ae-8c30-7d4aeabc2a7d'
client_id = 'd0868b64-0526-4d4a-9df0-3b521ae8e11a'
client_secret = 'YkG8Q~VyA0pAQswsGgYo0gEm_tEyKSyw_PIGJcr5'

authority_url = f'https://login.microsoftonline.com/{tenant_id}'
graph_api_url = 'https://graph.microsoft.com/v1.0/devices'

app = msal.ConfidentialClientApplication(
    client_id,
    authority=authority_url,
    client_credential=client_secret
)

token_response = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

if 'access_token' in token_response:
    access_token = token_response['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(graph_api_url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        with open('devices.json', 'w') as json_file:
            json.dump(devices, json_file, indent=4)
        print("Devices data saved to devices.json")
    else:
        print(f"Failed to retrieve devices: {response.status_code} - {response.text}")
else:
    print("Failed to acquire token")
    print(f"Error: {token_response.get('error')}")
    print(f"Error Description: {token_response.get('error_description')}")
    print(f"Error Codes: {token_response.get('error_codes')}")
    print(f"Correlation Id: {token_response.get('correlation_id')}")
    print(f"Claims: {token_response.get('claims')}")