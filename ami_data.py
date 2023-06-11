# !/usr/bin/python3
import boto3
import csv

session = boto3.Session(profile_name='default')

ec2_resource = session.resource('ec2')
ec2_client = session.client('ec2')

# amis = ec2_client.describe_images(Owners=['self'])
amis = ec2_resource.images.filter(Owners=['self'])

scraped_data = []

for ami in amis:
    ami_id = ami.id
    block_device_mappings = ami.block_device_mappings
    for block_device in block_device_mappings:
        device_id = block_device['DeviceName']
        
        # Retrieve snapshot information
        snapshot_id = block_device['Ebs']['SnapshotId']
        
        # Describe the snapshot to get DeleteOnTermination attribute
        snapshot = ec2_client.describe_snapshots(SnapshotIds=[snapshot_id])['Snapshots'][0]
        # delete_on_termination = snapshot['DeleteOnTermination']
        print(dir(snapshot))
        # Store the scraped data in a list
        # scraped_data.append([ami_id, device_id, delete_on_termination])

# print(scraped_data)
