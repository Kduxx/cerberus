import boto3
import os

APPLICATION_NAME = os.environ.get('APPLICATION_NAME')
api_gateway = boto3.client("apigateway")
cloudwatch_events = boto3.client("events")
DEFAULT_KEY_NAME = '{}TemporaryKey'.format(APPLICATION_NAME)

def handler(event, context):
    api_keys = api_gateway.get_api_keys(nameQuery=DEFAULT_KEY_NAME)['items']
    rule = event['resources'][0].split('/')[-1:][0]
    for api_key in api_keys:
        api_gateway.delete_api_key(apiKey=api_key['id'])

    targets = cloudwatch_events.list_targets_by_rule(Rule=rule)
    for target in targets['Targets']:
        cloudwatch_events.remove_targets(Rule=rule, Ids=[target['Id']])

    cloudwatch_events.delete_rule(Name=rule)
