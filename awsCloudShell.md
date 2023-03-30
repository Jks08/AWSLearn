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