import json
import boto3
import requests
from requests.auth import HTTPBasicAuth

def get_secret_information():
    # Specify the name or ARN of the secret
    secret_name = ""
    # Create a Secrets Manager client
    client = boto3.client("secretsmanager")
    
    try:
        # Retrieve the secret value
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])
        return secret
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}",
        }




def get_access_token_with_secret():
    results=""
    
    secret = get_secret_information()
    url = secret["domainurl"]
    client_id = secret["clientid"]
    client_secret = secret["clientsecret"]
    scope = secret["scope"]
    

    # Set up the headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Set up the payload
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'scope': scope
    }

    # Set up the basic authentication credentials
    auth = HTTPBasicAuth(client_id, client_secret)

    
    # Send the POST request
    response = requests.post(url, headers=headers, auth=auth, data=payload)

    # Check the response
    if response.status_code == 200:
        # Successful request
        data =  response.json()
        access_token = data['access_token']
        print('Access token:', access_token)
        results = getStatisticalCalculation(access_token)
    else:
        # Error occurred
        access_token=""
        print('Request failed with status code:', response.status_code)    
    return results    

def getStatisticalCalculation(access_token):
    # Set the API endpoint URL
    url = 'https://m6j6bm74dj.execute-api.ap-southeast-2.amazonaws.com'

    # Set the headers with the Authorization token
    headers = {
        'Authorization': access_token
    }

    # Send the GET request
    response = requests.get(url, headers=headers)
    # Check the response status code
    if response.status_code == 200:
        results=response.json()
        # Successful request
        print('Request successful!')
        print('---------------------------------------------------------------------')
        print(response.json())
    else:
        # Request failed
        print('Request failed with status code:', response.status_code)
        print('Response body:', response.text)
        results=""
    return results    


def lambda_handler(event, context):
    # TODO implement
    results=get_access_token_with_secret()
    return {
        'statusCode': 200,
        'body': json.dumps(str(results))
    }
