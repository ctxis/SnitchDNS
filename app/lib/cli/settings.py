import click
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.command('settings', help='Manage SnitchDNS settings')
@click.option('--action', required=False, default='get', show_default=True, help='Action to perform.', type=click.Choice(['get', 'set']))
@click.option('--name', required=True, help='Variable name', type=click.STRING)
@click.option('--value', required=False, default=None, help='Variable value', type=click.STRING)
@click.option('--default', required=False, default='', help='Default value to return if config does not exist', type=click.STRING)
@with_appcontext
def main(action, name, value, default):
    settings = Provider().settings()

    if action == 'get':
        print(settings.get(name, default))
    elif action == 'set':
        if value is None:
            print("Missing --value argument")
        else:
            settings.save(name, value)
            print('OK')

    return True
