#!/usr/bin/python3
import sys
import boto3

Environment = sys.argv[1]
QueueName = sys.argv[2]
DeadLetterQueueName = sys.argv[3]
MaxReceiveCount = sys.argv[4]
LOB = sys.argv[5]
REF_ID = sys.argv[6]
ApplicationName = sys.argv[7]
SNSTopicName = sys.argv[8]
SNSSubscriptionRequired = sys.argv[9]

# Now, we provision the SQS Queue and SNS Topic(if required) for the application using boto3
# Some Rules:
# 1. If SNSSubscriptionRequired is True, then we create a SNS Topic and subscribe the SQS Queue to it
# 2. If SNSSubscriptionRequired is False, then we create a SQS Queue and do not create a SNS Topic
# 3. If there is no value for DeadLetterQueueName, then we do not create a Dead Letter Queue and we do not include a RedrivePolicy in the SQS Queue
# 4. If there is a value for DeadLetterQueueName, then we create a Dead Letter Queue and we include a RedrivePolicy in the SQS Queue

# Create SQS client
sqs = boto3.client('sqs')

# Create SNS client
sns = boto3.client('sns')

# Create SQS Queue
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
    response = sqs.create_queue(
        QueueName=QueueName,
        tags = {
        'LOB': LOB,
        'REF_ID': REF_ID,
        'Application Name': ApplicationName
        },
        Attributes={
            'RedrivePolicy': '{"deadLetterTargetArn":"Fn::GetAtt": ["' + DeadLetterQueueName + '","Arn"],"maxReceiveCount":"' + MaxReceiveCount + '"}'
        }
    )
    # Create Dead Letter Queue
    response = sqs.create_queue(
        QueueName=DeadLetterQueueName,
        # No tags required for Dead Letter Queue
    )




# Print the number of arguments
# print(len(sys.argv))