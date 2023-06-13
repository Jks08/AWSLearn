import boto3
import csv

rds = boto3.client('rds')
dbs = rds.describe_db_instances()
for db in dbs['DBInstances']:
    try:
        print(f"{db['DBInstanceIdentifier']}")
    except:
        print("No DB Instances found")
        pass
    try:
        print(f" Backup Retention Period: {db['BackupRetentionPeriod']}")
    except:
        print("No Backup Retention Period found")
        pass
    try:
        print(f" Latest Restorable Time: {db['LatestRestorableTime']} in UTC")
    except:
        print("No Latest Restorable Time found")
        pass
    try:
        print(f" Copy Tags to Snapshots: {db['CopyTagsToSnapshot']}")
    except:
        print("No Copy Tags to Snapshots found")
        pass
    try:
        print(f" Backup Window: {db['PreferredBackupWindow']} in IST")
    except:
        print("No Backup Window found")
        pass
    print("\n")
