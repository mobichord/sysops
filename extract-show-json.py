import msal
import requests
import json

tenant_id = '41e9b618-6728-42ae-8c30-7d4aeabc2a7d'
client_id = 'd0868b64-0526-4d4a-9df0-3b521ae8e11a'
client_secret = 'YkG8Q~VyA0pAQswsGgYo0gEm_tEyKSyw_PIGJcr5'

authority_url = f'https://login.microsoftonline.com/{tenant_id}'
graph_api_url = 'https://graph.microsoft.com/v1.0/users'

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
        users = response.json().get('value', [])
        
        if users:
            first_user_id = users[0]['id']
            user_detail_url = f'https://graph.microsoft.com/v1.0/users/{first_user_id}?$select=aboutMe,accountEnabled,ageGroup,assignedLicenses,assignedPlans,birthday,city,companyName,consentProvidedForMinor,country,createdDateTime,creationType,customSecurityAttributes,deletedDateTime,department,displayName,employeeHireDate,employeeLeaveDateTime,employeeId,employeeOrgData,employeeType,externalUserState,externalUserStateChangeDateTime,faxNumber,givenName,hireDate,identities,imAddresses,interests,jobTitle,lastPasswordChangeDateTime,legalAgeGroupClassification,licenseAssignmentStates,mailNickname,mySite,onPremisesDistinguishedName,onPremisesDomainName,onPremisesExtensionAttributes,onPremisesImmutableId,onPremisesLastSyncDateTime,onPremisesProvisioningErrors,onPremisesSamAccountName,onPremisesSecurityIdentifier,onPremisesSyncEnabled,onPremisesUserPrincipalName,otherMails,passwordPolicies,passwordProfile,pastProjects,postalCode,preferredName,provisionedPlans,proxyAddresses,refreshTokensValidFromDateTime,responsibilities,serviceProvisioningErrors,schools,signInSessionsValidFromDateTime,skills,state,streetAddress,usageLocation,userPrincipalName,userType'
            
            user_response = requests.get(user_detail_url, headers=headers)
            if user_response.status_code == 200:
                user_data = user_response.json()
                print(json.dumps(user_data, indent=4))
            else:
                print(f"Failed to retrieve details for user {first_user_id}: {user_response.status_code} - {user_response.text}")
        else:
            print("No users found.")
    else:
        print(f"Failed to retrieve users: {response.status_code} - {response.text}")
else:
    print("Failed to acquire token")
    print(f"Error: {token_response.get('error')}")
    print(f"Error Description: {token_response.get('error_description')}")
    print(f"Error Codes: {token_response.get('error_codes')}")
    print(f"Correlation Id: {token_response.get('correlation_id')}")
    print(f"Claims: {token_response.get('claims')}")
