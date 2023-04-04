# Here we note down AWS Cloud Shell commands to be executed
"""
Starting with S3
AVAILABLE COMMANDS
       o cp

       o ls

       o mb

       o mv

       o presign

       o rb

       o rm

       o sync

       o website
"""

# 1. List all S3 buckets
aws s3 ls

# 2. Create a new S3 bucket
aws s3 mb s3://my-new-bucket

# 3. Go to specific S3 bucket
aws s3 ls s3://my-new-bucket

# 4. Delete a specific S3 bucket
aws s3 rb s3://my-new-bucket

# 5. Delete specific file from S3 bucket
aws s3 rm s3://my-new-bucket/my-file.txt

# 6. Copy a file from local to S3 bucket
aws s3 cp my-file.txt s3://my-new-bucket

# 7. Copy a file from S3 bucket to local
aws s3 cp s3://my-new-bucket/my-file.txt .

# 8. Copy a file from S3 bucket to another S3 bucket
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2

# 9. Copy a file from S3 bucket to another S3 bucket with a new name
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt

# 10. Copy a file from S3 bucket to another S3 bucket with a new name and make it private
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl private

# 11. Copy a file from S3 bucket to another S3 bucket with a new name and make it public
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl public-read

# 12. Copy a file from S3 bucket to another S3 bucket with a new name and make it public with a custom cache control
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl public-read --cache-control max-age=31536000

# 13. Copy a file from S3 bucket to another S3 bucket with a new name and make it public with a custom cache control and content type
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl public-read --cache-control max-age=31536000 --content-type text/html

# 14. Copy a file from S3 bucket to another S3 bucket with a new name and make it public with a custom cache control and content type and metadata
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl public-read --cache-control max-age=31536000 --content-type text/html --metadata '{"key1":"value1","key2":"value2"}'

# 15. Copy a file from S3 bucket to another S3 bucket with a new name and make it public with a custom cache control and content type and metadata and encryption
aws s3 cp s3://my-new-bucket/my-file.txt s3://my-new-bucket-2/my-file-2.txt --acl public-read --cache-control max-age=31536000 --content-type text/html --metadata '{"key1":"value1","key2":"value2"}' --sse

"""
Starting with EC2
"""

# 1. List all EC2 instances
aws ec2 describe-instances

# 2. List only names of EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value[]]' --output text

# 3. List only running EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value[]]' --output text --filters Name=instance-state-name,Values=running

# 4. List only stopped EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value[]]' --output text --filters Name=instance-state-name,Values=stopped

# 5. List only terminated EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value[]]' --output text --filters Name=instance-state-name,Values=terminated

# 6. Stop a specific EC2 instance
aws ec2 stop-instances --instance-ids <instance_id/name>

# 7. Start a specific EC2 instance
aws ec2 start-instances --instance-ids <instance_id/name>

# 8. Terminate a specific EC2 instance
aws ec2 terminate-instances --instance-ids <instance_id/name>

# 9. Create a new EC2 instance
aws ec2 run-instances --image-id <image_id> --count 1 --instance-type t2.micro --key-name <key_name> --security-group-ids <security_group_id> --subnet-id <subnet_id>

# 10. Create a new EC2 instance with a specific name
aws ec2 run-instances --image-id <image_id> --count 1 --instance-type t2.micro --key-name <key_name> --security-group-ids <security_group_id> --subnet-id <subnet_id> --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=<instance_name>}]'

# 11. Stop all EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --output text --filters Name=instance-state-name,Values=running | xargs -I {} aws ec2 stop-instances --instance-ids {}

# 12. Start all EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --output text --filters Name=instance-state-name,Values=stopped | xargs -I {} aws ec2 start-instances --instance-ids {}

# 13. Stop a specific EC2 instance
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --output text --filters Name=instance-state-name,Values=running | xargs -I {} aws ec2 stop-instances --instance-ids {}

# 14. Terminate all EC2 instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --output text --filters Name=instance-state-name,Values=running | xargs -I {} aws ec2 terminate-instances --instance-ids {}

# 15. Terminate a specific EC2 instance
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId]' --output text --filters Name=instance-state-name,Values=running | xargs -I {} aws ec2 terminate-instances --instance-ids {}

# 16. SSH into a specific EC2 instance
ssh -i <key_name>.pem ec2-user@<public_ip> 
(if no key_name, use ec2-user@<public_ip>)

"""
Starting with IAM
"""

# 1. List all IAM users
aws iam list-users

# 2. List all IAM users with their access keys
aws iam list-users --query 'Users[*].[UserName,AccessKeyIds]' --output text

# 3. List all IAM users with their access keys and their groups
aws iam list-users --query 'Users[*].[UserName,AccessKeyIds,Groups]' --output text

# 4. Delete a specific IAM user
a. aws iam delete-user --user-name <user_name> 
b. aws iam delete-login-profile --user-name <user_name>

# 5. Detach all policies from a specific IAM user
aws iam list-user-policies --user-name <user_name> --query 'PolicyNames[*]' --output text | xargs -I {} aws iam detach-user-policy --user-name <user_name> --policy-arn arn:aws:iam::aws:policy/{}

# 5. Create a new IAM user
aws iam create-user --user-name <user_name>

# 6. Create a new IAM user with a specific password
aws iam create-user --user-name <user_name>
aws iam create-login-profile --user-name <user_name> --password <password>