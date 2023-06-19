# # Delete Stack from parameters
# # !/usr/bin/python3
# import sys
# import boto3
# import json
# import botocore
# import re
# from botocore.exceptions import ClientError

# try:
#     Environment = sys.argv[1]
#     QueueName = sys.argv[2]
#     DeadLetterQueueName = sys.argv[3]
#     MaxReceiveCount = sys.argv[4]
#     LOB = sys.argv[5]
#     REF_ID = sys.argv[6] # For the parameter JIRA_ID
#     ApplicationName = sys.argv[7]
#     SNSTopicName = sys.argv[8]
#     SNSSubscriptionRequired = sys.argv[9]
#     QueueType = sys.argv[10]
#     # If QueueType is FIFO, then set QueueType to true else false
#     if QueueType == "FIFO":
#         QueueType = True
#     else:
#         QueueType = False
#     VisibilityTimeout = sys.argv[11]
#     MessageRetentionPeriod = sys.argv[12]
#     MaximumMessageSize = sys.argv[13]
#     DelaySeconds = sys.argv[14]
#     ReceiveMessageWaitTimeSeconds = sys.argv[15]
#     RawMessageDelivery = sys.argv[16]
#     Stackname = sys.argv[17]
# except IndexError:
#     print("Please provide all the required arguments: Environment, QueueName, DeadLetterQueueName, MaxReceiveCount, LOB, REF_ID, ApplicationName, SNSTopicName, SNSSubscriptionRequired, QueueType, VisibilityTimeout, MessageRetentionPeriod, MaximumMessageSize, DelaySeconds,RawMessageDelivery, Stackname")
#     sys.exit(1)

# try:
#     cfn = boto3.client('cloudformation')
#     response = cfn.delete_stack(
#         StackName=Stackname
#     )
# except ClientError as e:
#     print(e)
#     print("Stack deletion failed")
#     sys.exit(1)

    