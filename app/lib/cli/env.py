import click
from flask.cli import with_appcontext


@click.command('env', help='SnitchDNS helper to identify the running environment')
@with_appcontext
def main():
    print('OK')
    return True
