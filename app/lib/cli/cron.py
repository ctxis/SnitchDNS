import click
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.command('cron', help='SnitchDNS Cron')
@with_appcontext
def main():
    cron = Provider().cron()
    return cron.run()
