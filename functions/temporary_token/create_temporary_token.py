import boto3
import json
import datetime
import time
import os

APPLICATION_NAME=os.environ.get('APPLICATION_NAME')
api_gateway = boto3.client('apigateway')
lambda_function = boto3.client('lambda')
cloudwatch_events = boto3.client('events')
DEFAULT_KEY_NAME = "{}TemporaryKey".format(APPLICATION_NAME)
aws_account = boto3.client('sts').get_caller_identity().get('Account')

def handler(event, context):
    print('\n')
    api_keys = api_gateway.get_api_keys(nameQuery=DEFAULT_KEY_NAME)['items']
    for api_key in api_keys:
        delete_api_key(api_key['id'])
    created_key = create_api_key()

    response_body = {
        'RequestResult': {
            'Success': True,
            'Message': 'Temporary api key created. You have about 2 minute before it expires.',
            'Response': {'api_key': created_key}}}

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body)
}

def get_usage_plan_id():
    return [ x for x in api_gateway.get_usage_plans()['items'] if os.environ.get('APPLICATION_NAME') in x['name']][0]['id']

def create_api_key():
    response = api_gateway.create_api_key(name=DEFAULT_KEY_NAME, enabled=True)
    create_cloudwatch_event(response['createdDate'])
    api_gateway.create_usage_plan_key(
        usagePlanId=get_usage_plan_id(),
        keyId=response['id'],
        keyType='API_KEY'
    )
    return response['value']

def create_cloudwatch_event(created_date):
    limit = created_date + datetime.timedelta(minutes=2, seconds=8)
    rule = cloudwatch_events.put_rule(Name="{}TemporaryKeyLimit".format(APPLICATION_NAME), ScheduleExpression='cron({} {} * * ? *)'.format(limit.minute, limit.hour), State='ENABLED')
    targets = cloudwatch_events.list_targets_by_rule(Rule="{}TemporaryKeyLimit".format(APPLICATION_NAME))
    target = cloudwatch_events.put_targets(Rule='{}TemporaryKeyLimit'.format(APPLICATION_NAME),Targets=[{'Id':str(int(time.time())), 'Arn':'arn:aws:lambda:us-east-1:197209411573:function:{}-invalidate_token'.format(APPLICATION_NAME)}])
    response = lambda_function.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName='{}-invalidate_token'.format(APPLICATION_NAME),
        Principal='events.amazonaws.com',
        StatementId=str(int(time.time())),
    )

def delete_api_key(key_id):
    api_gateway.delete_api_key(apiKey=key_id)
