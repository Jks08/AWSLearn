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
    Action = sys.argv[18]
except IndexError:
    print("Please provide all the required arguments: Environment, QueueName, DeadLetterQueueName, MaxReceiveCount, LOB, REF_ID, ApplicationName, SNSTopicName, SNSSubscriptionRequired, QueueType, VisibilityTimeout, MessageRetentionPeriod, MaximumMessageSize, DelaySeconds,RawMessageDelivery, Stackname, Action")
    sys.exit(1)

# Now we create the CloudFormation stack
cloudformation = boto3.client('cloudformation')

try:
    stackNameNum = int(Stackname[-2::])
except ValueError:
    stackNameNum = 1

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

if Action == 'update':
    for resource in template['Resources']:
        try:
            if len(resource)<13 and template['Resources'][resource]['Properties']['QueueName'] == QueueName:
                print(resource)
                qName = template['Resources'][resource]['Properties']['QueueName']
                
                # For VisibilityTimeout
                if int(template['Resources'][resource]['Properties']['VisibilityTimeout']) != int(VisibilityTimeout):
                    template['Resources'][resource]['Properties']['VisibilityTimeout'] = int(VisibilityTimeout)
                    print(f"Updated VisibilityTimeout for {qName} to {VisibilityTimeout}")
                
                # For DelaySeconds
                if int(template['Resources'][resource]['Properties']['DelaySeconds']) != int(DelaySeconds):
                    template['Resources'][resource]['Properties']['DelaySeconds'] = int(DelaySeconds)
                    print(f"Updated DelaySeconds for {qName} to {DelaySeconds}")

                # For MessageRetentionPeriod
                if int(template['Resources'][resource]['Properties']['MessageRetentionPeriod']) != int(MessageRetentionPeriod):
                    template['Resources'][resource]['Properties']['MessageRetentionPeriod'] = int(MessageRetentionPeriod)
                    print(f"Updated MessageRetentionPeriod for {qName} to {MessageRetentionPeriod}")

                # For MaximumMessageSize
                if int(template['Resources'][resource]['Properties']['MaximumMessageSize']) != int(MaximumMessageSize):
                    template['Resources'][resource]['Properties']['MaximumMessageSize'] = int(MaximumMessageSize)
                    print(f"Updated MaximumMessageSize for {qName} to {MaximumMessageSize}")

                # For ReceiveMessageWaitTimeSeconds
                if int(template['Resources'][resource]['Properties']['ReceiveMessageWaitTimeSeconds']) != int(ReceiveMessageWaitTimeSeconds):
                    template['Resources'][resource]['Properties']['ReceiveMessageWaitTimeSeconds'] = int(ReceiveMessageWaitTimeSeconds)
                    print(f"Updated ReceiveMessageWaitTimeSeconds for {qName} to {ReceiveMessageWaitTimeSeconds}")

                # Now we print the template 
                print(json.dumps(template, indent=4))
                try:
                    update_stack = cloudformation.update_stack(
                        StackName=Stackname,
                        TemplateBody=json.dumps(template, indent=4),
                        )
                    print(f"Updating the stack {Stackname}")
                except botocore.exceptions.ClientError as e:
                    print(f"Exception: {e}")
                sys.exit(0) 
            else:
                print('No SQSQUEUE found in template')       
        except KeyError:
            pass


print(f"Length of Template: {len(json.dumps(template, indent=4))}")

if len(json.dumps(template, indent=4)) < 45000:
    print('Less than 51200')
    print(f'Updating same template with name: {Stackname}')

else:
    print('Greater than 51200')
    print('Cannot update this stack as it exceeds 51200')
    stackNameNum += 1
    Stackname = f"{Stackname[:-2]}{stackNameNum}"
    print(f'Creating new stack with name: {Stackname}')
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Template for creating SNS Topic and SQS Queue",
        "Parameters": {},
        "Mappings": {},
        "Conditions": {},
        "Resources": {}
    }


sqsQueueCount = 0
snsTopicCount = 0

# Find the number following "SQSQUEUE" and "SNSTOPIC" uder Resources
for resource in template['Resources']:
    if "SQSQUEUE" in resource:
        # Find the number following "SQSQUEUE"
        sqsQueueCount = int(re.findall(r'\d+', resource)[0])
    if "SNSTOPIC" in resource:
        # Find the number following "SNSTOPIC"
        snsTopicCount = int(re.findall(r'\d+', resource)[0])

sqsQueueCount += 2
snsTopicCount += 1

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
            f"SNSSUBSCRIPTION{snsTopicCount}SQSQUEUE{sqsQueueCount}": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "TopicArn": {
                        "Ref": existing_SNSTOPIC
                    },
                    "Endpoint": {
                        "Fn::GetAtt": [
                            f"SQSQUEUE{sqsQueueCount}",
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
            f"SNSTOPIC{snsTopicCount}": {
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
            f"SNSSUBSCRIPTION{snsTopicCount}SQSQUEUE{sqsQueueCount}": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "TopicArn": {
                        "Ref": f"SNSTOPIC{snsTopicCount}"
                    },
                    "Endpoint": {
                        "Fn::GetAtt": [
                            f"SQSQUEUE{sqsQueueCount}",
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
            f"SNSTOPIC{snsTopicCount}": {
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
        f"SQSQUEUE{sqsQueueCount-1}": {
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
        f"SQSQUEUE{sqsQueueCount}": {
            "Type": "AWS::SQS::Queue",
            "DependsOn": f"SQSQUEUE{sqsQueueCount-1}",
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
                            f"SQSQUEUE{sqsQueueCount-1}",
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
        f"SQSQUEUE{sqsQueueCount}": {
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
        f"SQSQUEUE{sqsQueueCount}POLICY": {
            "Type": "AWS::SQS::QueuePolicy",
            "Properties": {
                "Queues": [
                    {
                        "Ref": f"SQSQUEUE{sqsQueueCount}"
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
                                    f"SQSQUEUE{sqsQueueCount}",
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

# print(json.dumps(template, indent=4))

try:
    update_stack = cloudformation.update_stack(
        StackName=Stackname,
        TemplateBody=json.dumps(template, indent=4),
        )
    print(f"Updating the stack {Stackname}")
except botocore.exceptions.ClientError as e:
    create_stack = cloudformation.create_stack(
        StackName=Stackname,
        TemplateBody=json.dumps(template, indent=4),
        )
    print(f"Creating New Stack {Stackname}")