# !/usr/bin/python3
import sys
import boto3
import json
import rich

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
    print("Please provide all the required arguments: Environment, QueueName, DeadLetterQueueName, MaxReceiveCount, LOB, REF_ID, ApplicationName, SNSTopicName, SNSSubscriptionRequired")
    sys.exit(1)

sqs = boto3.client('sqs')
sns = boto3.client('sns')
queue_arn = None

# If Queue already exists, then we print the Queue URL and exit
try:
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
except KeyError:
    print("Queue does not exist. Creating Queue...")
    pass

# Now we build the CloudFormation template as a json file
# We will use the same template for both the CloudFormation and Boto3
# versions of this script
count = 1
resources_source_queue = {}
resources_dead_letter_queue = {}
resources_queue_policy = {}
resources_sns_topic = {}
resources_sns_subscription = {}

if SNSTopicName != "":
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
else:
    resources_sns_topic = None

if SNSSubscriptionRequired == "True":
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
                "RawMessageDelivery": "false"
            }
        }
    }
else:
    resources_sns_subscription = None

if "DeadLetterQueueName" != "":
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

if QueueName != "":
    resources_source_queue = {
        f"SQSQUEUE{count}": {
            "Type": "AWS::SQS::Queue",
            "DependsOn": f"SQSQUEUE{count-1}",
            "Properties": {
                "QueueName": QueueName,
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


template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Template for creating SNS Topic and SQS Queue",
    "Parameters": {},
    "Mappings": {},
    "Conditions": {},
    "Resources": {}
}


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


# with open('DirectProvisionCloudFormation.json', 'w') as outfile:
#     json.dump(template, outfile, indent=4)

# Print the template to the console using rich
rich.print(template)