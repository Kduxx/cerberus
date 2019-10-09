import boto3
import base64

def decrypt(event, context):
    encrypted = bytes(event['secret'], 'ascii')
    decoded = base64.b64decode(encrypted)
    kms = boto3.client('kms')
    decrypted = kms.decrypt(CiphertextBlob=decoded)
    return decrypted['Plaintext']
