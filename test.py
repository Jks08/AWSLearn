import boto3
import sys
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
    print("Error")
    print(e)
