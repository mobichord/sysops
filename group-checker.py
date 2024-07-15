import boto3
import json
import msal
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# Function to get secret from AWS Secrets Manager
def get_secret(secret_name):
    region_name = "us-west-2"

    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        raise e

    # Decrypts secret using the associated KMS key
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# Function to handle API requests with retry logic
def make_request_with_retries(url, headers, max_retries=5, backoff_factor=1):
    retries = 0
    while retries < max_retries:
        response = requests.get(url, headers=headers)
        if response.status_code == 429:  # Too Many Requests
            retries += 1
            wait_time = backoff_factor * (2 ** (retries - 1))
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            return response
    response.raise_for_status()  # Raise an error if the request failed after retries
    return response

# Retrieve secrets from AWS Secrets Manager
secrets = get_secret("ms-azure-api-keys")
tenant_id = secrets['tenant_id']
client_id = secrets['client_id']
client_secret = secrets['client_secret']

print(f"Using tenant_id: {tenant_id}")

authority_url = f'https://login.microsoftonline.com/{tenant_id}'
graph_api_url_groups = 'https://graph.microsoft.com/v1.0/groups'
graph_api_url_activities = 'https://graph.microsoft.com/v1.0/auditLogs/directoryAudits'

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

    # Retrieve list of groups
    response = make_request_with_retries(graph_api_url_groups, headers)

    if response.status_code == 200:
        groups = response.json()

        # Prepare to check activity
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)
        active_groups = []
        inactive_groups = []

        for group in groups['value']:
            group_id = group['id']
            group_name = group['displayName']

            # Check activity of each group over the past 30 days
            activity_query = f"{graph_api_url_activities}?$filter=activityDateTime ge {thirty_days_ago.isoformat()}Z and targetResources/any(r:r/id eq '{group_id}')"
            activity_response = make_request_with_retries(activity_query, headers)

            if activity_response.status_code == 200:
                activities = activity_response.json()
                if len(activities['value']) > 0:
                    active_groups.append({'Group ID': group_id, 'Group Name': group_name, 'Status': 'Active'})
                else:
                    inactive_groups.append({'Group ID': group_id, 'Group Name': group_name, 'Status': 'Inactive'})
            else:
                print(f"Failed to retrieve activity for group {group_name}: {activity_response.status_code} - {activity_response.text}")

        # Combine active and inactive groups
        all_groups = active_groups + inactive_groups

        # Convert to DataFrame and save to CSV
        df = pd.DataFrame(all_groups)
        df.to_csv('group_activity_status.csv', index=False)

        print("CSV file has been created: group_activity_status.csv")

    else:
        print(f"Failed to retrieve groups: {response.status_code} - {response.text}")
else:
    print("Failed to acquire token")
    print(f"Error: {token_response.get('error')}")
    print(f"Error Description: {token_response.get('error_description')}")
    print(f"Error Codes: {token_response.get('error_codes')}")
    print(f"Correlation Id: {token_response.get('correlation_id')}")
    print(f"Claims: {token_response.get('claims')}")
