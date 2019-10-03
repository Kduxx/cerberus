import os
import boto3
import json
import argparse

parser = argparse.ArgumentParser(description='Script used to configure the iam permissions to a existing or a user created by the script')

parser.add_argument('-u', '--user', type=str, required=True, help='The user name to attach the role with the necessary permissions')

args = parser.parse_args()

def add_permissions(user):
    iam = boto3.client('iam')
    policy_json = json.dumps(open('iam_policy.json', 'r').read())

    cerberus_group = iam.create_group(
        GroupName='CerberusGroup'
    )

    iam.add_user_to_group(
        GroupName=cerberus_group['Group']['GroupName'],
        UserName=user
    )

    cerberus_policy = iam.create_policy(
        PolicyName='CerberusPolicy',
        PolicyDocument=policy_json
    )

    policy_attachment = iam.attach_group_policy(
        GroupName=cerberus_group['Group']['GroupName'],
        PolicyArn=cerberus_policy['Policy']['Arn']
    )

if __name__ == '__main__':
    add_permissions(args.user)

