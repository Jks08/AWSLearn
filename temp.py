import re
import click
from flask.cli import with_appcontext
from flask import Flask

app = Flask(__name__)

@click.command(name='check_regex')
@with_appcontext
def check_regex():
    s1 = " new \r\n    jks       \r\nJKJSiHFUIEBK"
    # In s1 the first word is before the newline, the second word is after the newline. Use the re module to split the string into two words.
    s2 = re.split(r"\s+", s1)
    print(s2)

    # Modify the above to handle left and right whitespace and newline. Also, remove whitespace from the beginning and end of the string.
    s3 = re.sub(r"\s+", " ", s1)
    print(s3)

    # Why do we use only \s+ insead of \s+\r\n? Because \s+ matches any whitespace character, including the newline character.
    # \r is the carriage return character. It is used to move the cursor to the beginning of the line

@click.command(name='helloi')
def hello():
    print("Hello World")

@click.command('AWS_S3_list')
@with_appcontext
def AWS_S3_list():
    import boto3
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket.name)
        # This will not work because the AWS secret and access key were deactivated in the AWS console.

@click.command('sum_two_numbers')
@click.argument('x', type=int)
@click.argument('y', type=int)
@with_appcontext
def sum_two_numbers(x, y):
    print(x + y)


app.cli.add_command(check_regex)
app.cli.add_command(hello)
app.cli.add_command(AWS_S3_list)