import boto3
import csv

rds = boto3.client('rds')
dbs = rds.describe_db_instances()
rds = boto3.client('rds')
dbs = rds.describe_db_instances()
for db in dbs['DBInstances']:
    print(f"{db['DBInstanceIdentifier']} | {db['PreferredMaintenanceWindow']}")
