import re
import click
from flask.cli import with_appcontext
from flask import Flask

app = Flask(__name__)

@click.command(name='check_regex')
@with_appcontext
def check_regex():
    s1 = "jks       \r\nJKJSiHFUIEBK"
    # In s1 the first word is before the newline, the second word is after the newline. Use the re module to split the string into two words.
    s2 = re.split(r"\s+", s1)
    print(s2)

    # Why do we use only \s+ insead of \s+\r\n? Because \s+ matches any whitespace character, including the newline character.
    # \r is the carriage return character. It is used to move the cursor to the beginning of the line

@click.command(name='helloi')
def hello():
    print("Hello World")

app.cli.add_command(check_regex)
app.cli.add_command(hello)