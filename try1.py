#!/usr/bin/python3
import boto3

# Create an S3 client
s3 = boto3.client('s3')

# Call S3 to list current buckets
response = s3.list_buckets()

# Get a list of all bucket names from the response
buckets = [bucket['Name'] for bucket in response['Buckets']]
print("Bucket List: %s" % buckets)

# Create a bucket
# s3.create_bucket(Bucket='jksbuck')

# Create terraform configuration file
with open('terraform.tf', 'w') as f:
    f.write('provider "aws" { region = "us-east-1" }')