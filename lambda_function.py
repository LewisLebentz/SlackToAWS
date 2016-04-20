import boto3
from base64 import b64decode
from urlparse import parse_qs
import logging
ec2 = boto3.resource('ec2')

ENCRYPTED_EXPECTED_TOKEN = "xxxxxxxx" # Enter the base-64 encoded, encrypted Slack command token (CiphertextBlob)

kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob = b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    req_body = event['body']
    params = parse_qs(req_body)
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match exptected", token)
        raise Exception("Invalid request token")

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    command_text = params['text'][0]
    
    if command_text == 'now':
        ec2.create_instances(ImageId='ami-31328842', InstanceType="t2.micro", MinCount=1, MaxCount=1)
        return {'text': 'Starting an Amazon Linux t2.micro instance...'}
        
    if command_text == 'status':
        instances = ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        for instance in instances:
            list = list.append(instance.id, instance.instance_type)
        return list
    
    return "%s invoked %s in %s with the following text: %s" % (user, command, channel, command_text)
