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
queue_arn = None


def provision_sqs_sns_queue():
    global queue_arn
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
                return url, queue_arn
    except KeyError:
        print("Queue does not exist. Creating Queue...")

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
    global queue_arn
    for topic in sns.list_topics()['Topics']:
        if SNSTopicName in topic['TopicArn']:
            # Check if the SNS Topic has a subscription. If not, then subscribe.
            if SNSSubscriptionRequired == "True":
                subscriptions = sns.list_subscriptions_by_topic(
                    TopicArn=topic['TopicArn']
                )
                if subscriptions['Subscriptions'] == []:
                    response = sns.subscribe(
                        TopicArn=topic['TopicArn'],
                        Protocol='sqs',
                        Endpoint=queue_arn 
                    )
                    subscription_arn = response['SubscriptionArn']
                    print(f"Subscription created: {subscription_arn}")
                else:
                    print("Subscription already exists!")
            return topic['TopicArn']    
        
    try:
        
        if SNSTopicName != "":
            response = sns.create_topic(
                Name=SNSTopicName,
                Attributes={
                    'DisplayName': SNSTopicName
                },
                Tags=[
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
            if SNSSubscriptionRequired == "True":
                response = sns.subscribe(
                    TopicArn=topic_arn,
                    Protocol='sqs',
                    Endpoint=queue_arn 
                )

                subscription_arn = response['SubscriptionArn']
                print(f"SQS Queue subscribed to SNS Topic: {subscription_arn}")
            
            else:
                # This is the case when we want to create a new SNS Topic but not subscribe to it
                print("Not subscribing SQS Queue to SNS Topic as SNSSubscriptionRequired is False")

        else:
            print("Not creating SNS Topic as SNSTopicName is not provided")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if QueueName != "":
    print("Creating SQS Queue")
    print(provision_sqs_sns_queue())

if SNSSubscriptionRequired == "False":
    print("SNS Subscription not required")

if SNSTopicName == "":
    print("Not creating SNS Topic as SNSTopicName is not provided")

else:
    print("Creating SNS Topic")
    print(provision_sns_topic())