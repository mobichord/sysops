import requests
import json

okta_domain = ''
api_token = ''


okta_api_url = f'https://{okta_domain}/api/v1/users'


headers = {
    'Authorization': f'SSWS {api_token}',
    'Accept': 'application/json'
}

response = requests.get(okta_api_url, headers=headers)


if response.status_code == 200:
    users = response.json()
    with open('users.json', 'w') as json_file:
        json.dump(users, json_file, indent=4)
    print("Users data saved to users.json")
else:
    print(f"Failed to retrieve users: {response.status_code} - {response.text}")
