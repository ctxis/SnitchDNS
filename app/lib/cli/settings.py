import click
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.command('settings', help='Manage SnitchDNS settings')
@click.option('--action', required=False, default='get', show_default=True, help='Action to perform.', type=click.Choice(['get', 'set']))
@click.option('--name', required=True, help='Variable name', type=click.STRING)
@click.option('--value', required=False, default=None, help='Variable value', type=click.STRING)
@with_appcontext
def main(action, name, value):
    settings = Provider().settings()

    if action == 'get':
        print(settings.get(name))
    elif action == 'set':
        if value is None:
            print("Missing --value argument")
        else:
            settings.save(name, value)
            print('OK')

    return True
