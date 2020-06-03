import click


@click.command('env', help='SnitchDNS helper to identify the running environment')
def main():
    print('OK')
    return True
