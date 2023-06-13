import boto3
import csv

rds = boto3.client('rds')
dbs = rds.describe_db_instances()
for db in dbs['DBInstances']:
    try:
        print(f"{db['DBInstanceIdentifier']}")
        print(f" Backup Retention Perios: {db['BackupRetentionPeriod']}")
        print(f" Latest Restorable Time: {db['LatestRestorableTime']} in UTC")
        print(f" Copy Tags to Snapshots: {db['CopyTagsToSnapshot']}")
        print(f" Backup Window: {db['PreferredBackupWindow']} in IST")
        print("\n")
    except KeyError:
        pass
