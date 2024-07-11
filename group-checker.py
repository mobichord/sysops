import msal
import requests

tenant_id = '41e9b618-6728-42ae-8c30-7d4aeabc2a7d'
client_id = 'd0868b64-0526-4d4a-9df0-3b521ae8e11a'
client_secret = 'YkG8Q~VyA0pAQswsGgYo0gEm_tEyKSyw_PIGJcr5'
 
authority_url = f'https://login.microsoftonline.com/{tenant_id}'

app = msal.ConfidentialClientApplication(
    client_id,
    authority=authority_url,
    client_credential=client_secret
)

token_response = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])

if 'access_token' in token_response:
    access_token = token_response['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    
#    response = requests.get(f'https://graph.microsoft.com/v1.0/groups/{group_id}/drive/root', headers=headers)

    response = requests.get('https://graph.microsoft.com/v1.0/groups?$filter=groupTypes/any(c:c eq \'Unified\')', headers=headers)
    
    if response.status_code == 200:
        groups = response.json().get('value', [])

        # List and print groups and group IDs.
        for group in groups:
            print(f'Group Name: {group.get("displayName")}, Group ID: {group.get("id")}')
    else:
        print(f'Error: {response.status_code}, {response.text}')

 #   if response.status_code == 200:
 #       last_modified_date = response.json().get('lastModifiedDateTime')
 #       print(f'Last Modified Date: {last_modified_date}')
 #       from datetime import datetime, timedelta
 #       last_modified_datetime = datetime.fromisoformat(last_modified_date[:-1])
 #       if datetime.utcnow() - last_modified_datetime > timedelta(days=30):
 #           print('Group is inactive')
 #   else:
 #       print(f'Error: {response.status_code}, {response.text}')
else:
    print(f'Error acquiring token: {token_response.get("error_description")}')
