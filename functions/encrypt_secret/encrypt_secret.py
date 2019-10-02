import boto3
import base64
import os

def encrypt(event, context):
    secret = event['secret']
    kms = boto3.client('kms')
    encrypted = kms.encrypt(
        KeyId='alias/{}Protection'.format(os.environ.get('APPLICATION_NAME')),
        Plaintext=bytes(secret, 'utf-8')
    )
    return base64.b64encode(encrypted['CiphertextBlob'])

