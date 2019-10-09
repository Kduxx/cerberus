import os
import boto3
import json
import argparse

GROUP_NAME = "CerberusGroup"
POLICY_NAME = "CerberusPolicy"

parser = argparse.ArgumentParser(description='Script used to configure the iam permissions to a existing or a user created by the script')

parser.add_argument('-u', '--user', type=str, required=True, help='The user name to attach the role with the necessary permissions')

parser.add_argument('-p', '--profile', type=str, help='The profile used to create the group and policy')

args = parser.parse_args()

def group_exists(group_name):
    try:
        boto3.client('iam').get_group(GroupName=group_name)
        return True
    except:
        return False

def policy_exists(policy_arn):
    try:
        boto3.client('iam').get_policy(PolicyArn=policy_arn)
        return True
    except:
        return False

def add_permissions(user):
    iam = boto3.client('iam')
    policy_json = json.loads(open('iam_policy.json', 'r').read())
    if group_exists(GROUP_NAME):
        group_users = iam.get_group(GroupName=GROUP_NAME)["Users"]
        if len(group_users) > 0:
            print("Removing {} from {}".format(user, GROUP_NAME))
            for group_user in group_users:
                iam.remove_user_from_group(UserName=group_user['UserName'], GroupName=GROUP_NAME)
        group_policies = iam.list_attached_group_policies(GroupName=GROUP_NAME)
        print("Detaching policy(ies): {}".format(",".join([policy["PolicyName"] for policy in group_policies["AttachedPolicies"]])))
        for group_policy in group_policies["AttachedPolicies"]:
            iam.detach_group_policy(GroupName=GROUP_NAME, PolicyArn=group_policy["PolicyArn"])
        iam.delete_group(GroupName=GROUP_NAME)
        print("Deleting {}".format(GROUP_NAME))

    policy_arn = "arn:aws:iam::{}:policy/{}".format(aws_account, POLICY_NAME)
    if policy_exists(policy_arn):
        print("Deleting {}".format(POLICY_NAME))
        iam.delete_policy(PolicyArn=policy_arn)

    cerberus_group = iam.create_group(
        GroupName='CerberusGroup'
    )
    print("{} created".format(GROUP_NAME))

    iam.add_user_to_group(
        GroupName=cerberus_group['Group']['GroupName'],
        UserName=user
    )

    print("{} added to group".format(user))


    cerberus_policy = iam.create_policy(
        PolicyName=POLICY_NAME,
        PolicyDocument=json.dumps(policy_json)
    )
    print("{} created".format(POLICY_NAME))

    policy_attachment = iam.attach_group_policy(
        GroupName=cerberus_group['Group']['GroupName'],
        PolicyArn=cerberus_policy['Policy']['Arn']
    )

    print("{} attached to {}".format(POLICY_NAME, GROUP_NAME))

if __name__ == '__main__':
    if args.profile != "":
        boto3.setup_default_session(profile_name = args.profile)
        aws_account = boto3.client('sts').get_caller_identity()['Account']
    add_permissions(args.user)

