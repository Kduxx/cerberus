import boto3
import base64
from boto3 import resource
from boto3.dynamodb.conditions import Key, Attr
import json
import os

APPLICATION_NAME=os.environ.get('APPLICATION_NAME')
dynamodb = resource("dynamodb")
secrets_table = dynamodb.Table('{}Secrets'.format(APPLICATION_NAME)

def handler(event, context):

    url_parameters = event['queryStringParameters']

    if url_parameters:

        secret_title = url_parameters['secret_title'] or None

        result = query_secret(secret_title)

        return{

            'statusCode': result['status_code'],
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'RequestResult':
                {
                    'Success': result['success'],
                    'Message': result['message'],
                    'FoundSecrets': result['body']
                }
            })
        }

    else:

        return{

            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'RequestResult': {

                    'Success': False,
                    'Message': 'You did not specify any parameter',
                    'FoundSecrets': None

                }
            })
        }

def query_secret(secret_title):

    if secret_title:
        query_result = secrets_table.scan(FilterExpression=Attr('search_name').contains(secret_title.lower().replace(' ', '_')))
        return {
            'success': True,
            'message': 'Query executed successfully',
            'status_code': 200,
            'body': [ decrypt_secret(item) for item in query_result['Items']]
        }
    else:

        return {
            'success': False,
            'message': 'You have to specify the secret title',
            'status_code': 400,
            'body': None
        }

def decrypt_secret(item):
    secret = boto3.client('lambda').invoke(
        FunctionName='{}-decrypt_secret'.format(os.environ.get('APPLICATION_NAME'),
        Payload=json.dumps({'secret': item['secret']})
    )['Payload'].read().decode('utf-8')
    print(secret)
    item['secret'] = secret
    return item

