import click
import tabulate
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.group('settings', help='SnitchDNS Setting Management')
@with_appcontext
def main():
    pass


@main.command('list')
@with_appcontext
def cli_settings_list():
    settings = Provider().settings()

    headers = ['name', 'value']
    table = []
    for name, value in settings.all().items():
        table.append([
            name,
            value
        ])

    print(tabulate.tabulate(table, headers))
    return True


@main.command('get')
@click.option('--name', required=True, help='Config variable name', type=click.STRING)
@click.option('--default', required=False, default='', help='Default value to return if config does not exist', type=click.STRING)
@with_appcontext
def cli_settings_get(name, default):
    settings = Provider().settings()

    print(settings.get(name, default))
    return True


@main.command('set')
@click.option('--name', required=True, help='Config variable name', type=click.STRING)
@click.option('--value', required=True, help='Config variable value', type=click.STRING)
@with_appcontext
def cli_settings_get(name, value):
    settings = Provider().settings()

    settings.save(name, value)
    print("OK")
    return True
