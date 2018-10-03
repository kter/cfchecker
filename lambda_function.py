# import json
# TODO Add test
import boto3
import os
import json
import logging
import boto3
from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

print('Loading function')


class Slack:

    def __init__(self, channel, color, username, icon_url):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        ssm = boto3.client('ssm')
        ssm_response = ssm.get_parameters(
            Names=[
                os.getenv('SlackWebHookUrl'), ],
            WithDecryption=True
        )
        self.hook_url = ssm_response['Parameters'][0]['Value']
        self.channel = channel
        self.color = color
        self.username = username
        self.icon_url = icon_url

    def post(self, pretext, text, fields):
        slack_message={
            'pretext': pretext,
            'channel': self.channel,
            'text': text,
            'color': self.color,
            'username': self.username,
            'icon_url': self.icon_url,
            'fields': fields
        }
        req = Request(self.hook_url, json.dumps(slack_message).encode('utf-8'))
        try:
            response = urlopen(req)
            response.read()
            self.logger.info("Message posted to %s", slack_message['channel'])
        except HTTPError as e:
            self.logger.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            self.logger.error("Server connection failed: %s", e.reason)


def lambda_handler(event, context):
    slack = Slack(os.getenv('slackChannel'), '#36a64f', 'cfchecker', 'https://example.com/icon.jpg')
    client = boto3.client('cloudformation')
    response = client.describe_stacks()
    for stack in response['Stacks']:
        trigger_status = [x.strip() for x in str(os.getenv('TRIGGER_STATUS')).split(',')]
        if stack['StackStatus'] in trigger_status:
            alert_str = "Name: %s, Status: %s" % (stack['StackName'], stack['StackStatus'])
            print(alert_str)

            fields = [
                {
                    'title': 'スタック名',
                    'value': alert_str
                }
            ]
            slack.post('CloudFormation ステータス異常', 'CloudFormationのステータスが異常です。修正をお願いします。', fields)
