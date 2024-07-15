import boto3
import json
import msal
import requests
import pandas as pd

def get_secret(secret_name):
    region_name = "us-west-2"

    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

secrets = get_secret("ms-azure-api-keys")
tenant_id = secrets['tenant_id']
client_id = secrets['client_id']
client_secret = secrets['client_secret']

print(f"Using tenant_id: {tenant_id}")

authority_url = f'https://login.microsoftonline.com/{tenant_id}'
graph_api_url = 'https://graph.microsoft.com/v1.0/subscribedSkus'

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
        licenses = response.json()
        
        df = pd.json_normalize(licenses['value'])
        df.to_csv('licenses.csv', index=False)

        print("CSV file has been created: licenses.csv")

    else:
        print(f"Failed to retrieve licenses: {response.status_code} - {response.text}")
else:
    print("Failed to acquire token")
    print(f"Error: {token_response.get('error')}")
    print(f"Error Description: {token_response.get('error_description')}")
    print(f"Error Codes: {token_response.get('error_codes')}")
    print(f"Correlation Id: {token_response.get('correlation_id')}")
    print(f"Claims: {token_response.get('claims')}")
