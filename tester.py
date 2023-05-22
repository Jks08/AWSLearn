# !/usr/bin/python3
import sys
import boto3
import json
import botocore
import re
from botocore.exceptions import ClientError

try:
    Environment = sys.argv[1]
    QueueName = sys.argv[2]
    DeadLetterQueueName = sys.argv[3]
    MaxReceiveCount = sys.argv[4]
    LOB = sys.argv[5]
    REF_ID = sys.argv[6] # For the parameter JIRA_ID
    ApplicationName = sys.argv[7]
    SNSTopicName = sys.argv[8]
    SNSSubscriptionRequired = sys.argv[9]
    QueueType = sys.argv[10]
    # If QueueType is FIFO, then set QueueType to true else false
    if QueueType == "FIFO":
        QueueType = True
    else:
        QueueType = False
    VisibilityTimeout = sys.argv[11]
    MessageRetentionPeriod = sys.argv[12]
    MaximumMessageSize = sys.argv[13]
    DelaySeconds = sys.argv[14]
    ReceiveMessageWaitTimeSeconds = sys.argv[15]
    RawMessageDelivery = sys.argv[16]
    Stackname = sys.argv[17]
except IndexError:
    print("Please provide all the required arguments: Environment, QueueName, DeadLetterQueueName, MaxReceiveCount, LOB, REF_ID, ApplicationName, SNSTopicName, SNSSubscriptionRequired, QueueType, VisibilityTimeout, MessageRetentionPeriod, MaximumMessageSize, DelaySeconds,RawMessageDelivery, Stackname")
    sys.exit(1)

print(f"Environment: {Environment}")
print(f"QueueName: {QueueName}")
print(f"DeadLetterQueueName: {DeadLetterQueueName}")
print(f"MaxReceiveCount: {MaxReceiveCount}")
print(f"LOB: {LOB}")
print(f"REF_ID: {REF_ID}")
print(f"ApplicationName: {ApplicationName}")
print(f"SNSTopicName: {SNSTopicName}")
print(f"SNSSubscriptionRequired: {SNSSubscriptionRequired}")
print(f"QueueType: {QueueType}")
print(f"VisibilityTimeout: {VisibilityTimeout}")
print(f"MessageRetentionPeriod: {MessageRetentionPeriod}")
print(f"MaximumMessageSize: {MaximumMessageSize}")
print(f"DelaySeconds: {DelaySeconds}")
print(f"ReceiveMessageWaitTimeSeconds: {ReceiveMessageWaitTimeSeconds}")
print(f"RawMessageDelivery: {RawMessageDelivery}")
print(f"Stackname: {Stackname}")

# Now we create the CloudFormation stack
cloudformation = boto3.client('cloudformation')

# Print list of stacks containing SNS-SQS in the name
try:
    for stack in cloudformation.list_stacks()['StackSummaries']:
        if "SNS-SQS" in stack['StackName']:
            print(stack['StackName'])
except KeyError:
    print("No stacks found with SNS-SQS in the name")
    pass

# Get the template using the stack name
try:
    template_cft = cloudformation.get_template(StackName=Stackname)
except botocore.exceptions.ClientError as e:
    print(e.response['Error']['Message'])
    pass

# Get the Resources section of the template
try:
    template = dict(template_cft['TemplateBody'])
    # print(template)
    
except Exception:
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Template for creating SNS Topic and SQS Queue",
        "Parameters": {},
        "Mappings": {},
        "Conditions": {},
        "Resources": {}
    }
    # print(template['Resources'])

# Find the largest number in the SQSQUEUE resource name

numlist = []
for resource in template['Resources']:
    num = re.findall(r'\d+', resource)
    if num:
        numlist.append(num)
try:
    if len(DeadLetterQueueName) == 0:
        count = int(max(numlist)[0]) + 1
    else:
        count = int(max(numlist)[0]) + 2
except ValueError:
    count = 1

print(count)

# Find the number following "SQSQUEUE" and "SNSTOPIC" uder Resources
for resource in template['Resources']:
    if "SQSQUEUE" in resource:
        if template['Resources'][f"{resource}"]["Properties"]['QueueName']==QueueName:
            existing_SQSQUEUE = resource
    if "SNSTOPIC" in resource:
        if template['Resources'][f"{resource}"]["Properties"]['TopicName']==SNSTopicName:
            existing_SNSTOPIC = resource

print(existing_SQSQUEUE)
print(existing_SNSTOPIC)

resources_source_queue = {}
resources_dead_letter_queue = {}
resources_queue_policy = {}
resources_sns_topic = {}
resources_sns_subscription = {}

sqs = boto3.client('sqs')
sns = boto3.client('sns')
queue_arn = None

# If Queue already exists, then we print the Queue URL and exit
try:
    for url in sqs.list_queues()['QueueUrls']:
        # Need to check if the exact QueueName exists
        if QueueName == url.split('/')[-1]:
            queue_attributes = sqs.get_queue_attributes(
                QueueUrl=url,
                AttributeNames=['QueueArn']
                )
            queue_arn = queue_attributes['Attributes']['QueueArn']
            print(f"Queue already exists!")
            print(f"Queue URL: {url}")
            print(f"Queue ARN: {queue_arn}")
            sys.exit(0)
except KeyError:
    print("Queue does not exist. Creating Queue...")
    pass

snsList = []
if SNSTopicName != "":
    for topic in sns.list_topics()['Topics']:
        snsList.append(topic['TopicArn'].split(':')[-1])

for resource in template['Resources']:
    if "SNSTOPIC" in resource:
        if template['Resources'][f"{resource}"]["Properties"]['TopicName']==SNSTopicName:
            existing_SNSTOPIC = resource

if SNSTopicName != "" and SNSSubscriptionRequired == "True":
    if SNSTopicName in snsList:
        print(f"SNS Topic already exists!")
        resources_sns_subscription = {
            f"SNSSUBSCRIPTION{count}SQSQUEUE{count}": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "TopicArn": {
                        "Ref": existing_SNSTOPIC
                    },
                    "Endpoint": {
                        "Fn::GetAtt": [
                            f"SQSQUEUE{count}",
                            "Arn"
                        ]
                    },
                    "Protocol": "sqs",
                    "RawMessageDelivery": RawMessageDelivery
                }
            }
        }

    else:
        print(f"Creating SNS Topic and Subscription...")
        resources_sns_topic = {
            f"SNSTOPIC{count}": {
                "Type": "AWS::SNS::Topic",
                "Properties": {
                    "TopicName": SNSTopicName,
                    "Tags": [
                        {
                            "Key": "LOB",
                            "Value": LOB
                        },
                        {
                            "Key": "REF_ID",
                            "Value": REF_ID
                        },
                        {
                            "Key": "Application Name",
                            "Value": ApplicationName
                        }
                    ]
                }
            }
        }

        resources_sns_subscription = {
            f"SNSSUBSCRIPTION{count}SQSQUEUE{count}": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "TopicArn": {
                        "Ref": f"SNSTOPIC{count}"
                    },
                    "Endpoint": {
                        "Fn::GetAtt": [
                            f"SQSQUEUE{count}",
                            "Arn"
                        ]
                    },
                    "Protocol": "sqs",
                    "RawMessageDelivery": RawMessageDelivery
                }
            }
        }

elif SNSTopicName != "" and SNSSubscriptionRequired == "False":
    if SNSTopicName in snsList:
        print(f"SNS Topic already exists!")
        resources_sns_subscription = None
        resources_sns_topic = None
        pass
    else:
        print(f"Creating SNS Topic...")
        resources_sns_topic = {
            f"SNSTOPIC{count}": {
                "Type": "AWS::SNS::Topic",
                "Properties": {
                    "TopicName": SNSTopicName,
                    "Tags": [
                        {
                            "Key": "LOB",
                            "Value": LOB
                        },
                        {
                            "Key": "REF_ID",
                            "Value": REF_ID
                        },
                        {
                            "Key": "Application Name",
                            "Value": ApplicationName
                        }
                    ]
                }
            }
        }
        resources_sns_subscription = None

else:
    resources_sns_topic = None
    resources_sns_subscription = None

if len(DeadLetterQueueName) != 0:
    resources_dead_letter_queue = {
        f"SQSQUEUE{count-1}": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": DeadLetterQueueName
            }
        }
    }
else:
    resources_dead_letter_queue = None

if QueueName != "" and len(DeadLetterQueueName) != 0:
    # print("Both QueueName and DeadLetterQueueName are provided")
    resources_source_queue = {
        f"SQSQUEUE{count}": {
            "Type": "AWS::SQS::Queue",
            "DependsOn": f"SQSQUEUE{count-1}",
            "Properties": {
                "QueueName": QueueName,
                # "FifoQueue": QueueType,
                "VisibilityTimeout" : VisibilityTimeout,
                "DelaySeconds": DelaySeconds,
                "MessageRetentionPeriod": MessageRetentionPeriod,
                "MaximumMessageSize": MaximumMessageSize,
                "ReceiveMessageWaitTimeSeconds": ReceiveMessageWaitTimeSeconds,
                "RedrivePolicy": {
                    "deadLetterTargetArn": {
                        "Fn::GetAtt": [
                            f"SQSQUEUE{count-1}",
                            "Arn"
                        ]
                    },
                    "maxReceiveCount": MaxReceiveCount
                },
                "Tags": [
                    {
                        "Key": "LOB",
                        "Value": LOB
                    },
                    {   
                        "Key": "REF_ID",
                        "Value": REF_ID
                    },
                    {
                        "Key": "Application Name",
                        "Value": ApplicationName
                    }
                ]
            }
        }
    }

elif QueueName != "" and len(DeadLetterQueueName) == 0:
    # print("Only Source QueueName is provided")
    resources_source_queue = {
        f"SQSQUEUE{count}": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "QueueName": QueueName,
                # "FifoQueue": QueueType,
                "VisibilityTimeout" : VisibilityTimeout,
                "DelaySeconds": DelaySeconds,
                "MessageRetentionPeriod": MessageRetentionPeriod,
                "MaximumMessageSize": MaximumMessageSize,
                "ReceiveMessageWaitTimeSeconds": ReceiveMessageWaitTimeSeconds,
                "Tags": [
                    {
                        "Key": "LOB",
                        "Value": LOB
                    },
                    {   
                        "Key": "REF_ID",
                        "Value": REF_ID
                    },
                    {
                        "Key": "Application Name",
                        "Value": ApplicationName
                    }
                ]
            }
        }
    }

else:
    resources_source_queue = None

if QueueName != "":
    resources_queue_policy = {
        f"SQSQUEUE{count}POLICY": {
            "Type": "AWS::SQS::QueuePolicy",
            "Properties": {
                "Queues": [
                    {
                        "Ref": f"SQSQUEUE{count}"
                    }
                ],
                "PolicyDocument": {
                    "Statement": [
                        {
                            "Action": "SQS:*",
                            "Effect": "Allow",
                            "Principal": "*",
                            "Resource": {
                                "Fn::GetAtt": [
                                    f"SQSQUEUE{count}",
                                    "Arn"
                                ]
                            }
                        }
                    ]
                }
            }
        }
    }
else:
    resources_queue_policy = None


if resources_sns_topic != None:
    template["Resources"].update(resources_sns_topic)

if resources_dead_letter_queue != None:
    template["Resources"].update(resources_dead_letter_queue)

if resources_source_queue != None:
    template["Resources"].update(resources_source_queue)

if resources_queue_policy != None:
    template["Resources"].update(resources_queue_policy)

if resources_sns_subscription != None:
    template["Resources"].update(resources_sns_subscription)

print(json.dumps(template, indent=4))

# try:
#     update_stack = cloudformation.update_stack(
#         StackName=Stackname,
#         TemplateBody=json.dumps(template, indent=4),
#         )
#     print(f"Updating the stack {Stackname}")
# except botocore.exceptions.ClientError as e:
#     create_stack = cloudformation.create_stack(
#         StackName=Stackname,
#         TemplateBody=json.dumps(template, indent=4),
#         )
#     print(f"Creating New Stack {Stackname}")
