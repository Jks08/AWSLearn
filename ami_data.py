import boto3
import csv

rds = boto3.client('rds')
dbs = rds.describe_db_instances()
for db in dbs['DBInstances']:
    try:
        print(f"{db['DBInstanceIdentifier']}")
    except:
        print("No DB Instances found")
        continue
    try:
        print(f" Backup Retention Perios: {db['BackupRetentionPeriod']}")
    except:
        print("No Backup Retention Period found")
        continue
    try:
        print(f" Latest Restorable Time: {db['LatestRestorableTime']} in UTC")
    except:
        print("No Latest Restorable Time found")
        continue
    try:
        print(f" Copy Tags to Snapshots: {db['CopyTagsToSnapshot']}")
    except:
        print("No Copy Tags to Snapshots found")
        continue
    try:
        print(f" Backup Window: {db['PreferredBackupWindow']} in IST")
    except:
        print("No Backup Window found")
        continue
    print("\n")
