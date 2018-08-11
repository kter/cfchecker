# import json
# TODO Add test
import boto3
import os

print('Loading function')


def lambda_handler(event, context):
    client = boto3.client('cloudformation')
    response = client.describe_stacks()
    for stack in response['Stacks']:
        trigger_status = [x.strip() for x in str(os.getenv('TRIGGER_STATUS')).split(',')]
        if stack['StackStatus'] in trigger_status:
            print("Name: %s, Status: %s" % (stack['StackName'], stack['StackStatus']))
