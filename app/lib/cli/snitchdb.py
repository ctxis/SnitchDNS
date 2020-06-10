import click
from flask.cli import with_appcontext
from app.lib.database.seed import SeedDatabase


@click.command('snitchdb', help='SnitchDNS Database Setup')
@with_appcontext
def main():
    seed = SeedDatabase()
    seed.run()
    return True
