# !/usr/bin/python3
import sys
import boto3
import json

try:
    Environment = sys.argv[1]
    QueueName = sys.argv[2]
    DeadLetterQueueName = sys.argv[3]
    MaxReceiveCount = sys.argv[4]
    LOB = sys.argv[5]
    REF_ID = sys.argv[6]
    ApplicationName = sys.argv[7]
    SNSTopicName = sys.argv[8]
    SNSSubscriptionRequired = sys.argv[9]
except IndexError:
    print("Please provide all the required arguments")
    sys.exit(1)

sqs = boto3.client('sqs')
sns = boto3.client('sns')
queue_arn = None

# If Queue already exists, then we print the Queue URL and exit
for url in sqs.list_queues()['QueueUrls']:
    if QueueName in url:
        queue_attributes = sqs.get_queue_attributes(
            QueueUrl=url,
            AttributeNames=['QueueArn']
            )
        queue_arn = queue_attributes['Attributes']['QueueArn']
        print(f"Queue already exists!")
        print(f"Queue URL: {url}")
        print(f"Queue ARN: {queue_arn}")
        sys.exit(0)

# Now we build the CloudFormation template as a json file
# We will use the same template for both the CloudFormation and Boto3
# versions of this script

resources_source_queue = {}
resources_dead_letter_queue = {}
resources_sns_topic = {}
resources_sns_subscription = {}




template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Template for creating SNS Topic and SQS Queue",
    "Parameters": {},
    "Mappings": {},
    "Conditions": {},
    "Resources": {
    
    }
}