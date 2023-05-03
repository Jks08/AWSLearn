#!/usr/bin/python3
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

# Now, we provision the SQS Queue and SNS Topic(if required) for the application using boto3
# Some Rules:
# 1. If SNSSubscriptionRequired is True, then we create a SNS Topic and subscribe the SQS Queue to it
# 2. If SNSSubscriptionRequired is False, then we create a SQS Queue and do not create a SNS Topic
# 3. If there is no value for DeadLetterQueueName, then we do not create a Dead Letter Queue and we do not include a RedrivePolicy in the SQS Queue
# 4. If there is a value for DeadLetterQueueName, then we create a Dead Letter Queue and we include a RedrivePolicy in the SQS Queue
def provision_sqs_sns_queue():
    try:
        if DeadLetterQueueName == "":
            response = sqs.create_queue(
                QueueName=QueueName,
                tags={
                'LOB': LOB,
                'REF_ID': REF_ID,
                'Application Name': ApplicationName
                }
            )

        else:
            dead_letter_queue_response = sqs.create_queue(
                QueueName=DeadLetterQueueName
            )
            dead_letter_queue_url = dead_letter_queue_response['QueueUrl']
            queue_attributes = sqs.get_queue_attributes(
                QueueUrl=dead_letter_queue_url,
                AttributeNames=['QueueArn']
                )
            queue_arn = queue_attributes['Attributes']['QueueArn']
            print(f"Dead Letter Queue created: {queue_arn}")

            # Create Main Queue with Redrive Policy
            response = sqs.create_queue(
                QueueName=QueueName,
                tags={
                    'LOB': LOB,
                    'REF_ID': REF_ID,
                    'Application Name': ApplicationName
                },
                Attributes={
                    'RedrivePolicy': json.dumps({
                        'deadLetterTargetArn': queue_arn,
                        'maxReceiveCount': '3'
                    })
                }
            )
            queue_url = response['QueueUrl']
            print(f"Main Queue created with Redrive Policy: {queue_url}")
    
    except Exception as e:
        print(f"Error is {e}")
        sys.exit(1)

def provision_sns_topic():
    try:
        if SNSSubscriptionRequired == "True":
            response = sns.create_topic(
                Name=SNSTopicName,
                Attributes={
                    'DisplayName': SNSTopicName
                },
                tags=[
                    {
                        'Key': 'LOB',
                        'Value': LOB
                    },
                    {
                        'Key': 'REF_ID',
                        'Value': REF_ID
                    },
                    {
                        'Key': 'Application Name',
                        'Value': ApplicationName
                    }
                ]
            )
            topic_arn = response['TopicArn']
            print(f"SNS Topic created: {topic_arn}")

            # Subscribe SQS Queue to SNS Topic
            response = sns.subscribe(
                TopicArn=topic_arn,
                Protocol='sqs',
                Endpoint=QueueName
            )
            subscription_arn = response['SubscriptionArn']
            print(f"SQS Queue subscribed to SNS Topic: {subscription_arn}")

        else:
            print("No SNS Topic created")
    except Exception as e:
        print(f"Error is {e}")
        sys.exit(1)

if QueueName != "":
    provision_sqs_sns_queue()

if SNSTopicName != "":
    provision_sns_topic()