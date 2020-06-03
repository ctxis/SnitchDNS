import click


@click.command('snitch_env', help='This is a helper to identify the running environment')
def main():
    print('OK')
    return True
