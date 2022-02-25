import click
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.command('snitch_daemon', help='SnitchDNS Daemon')
@click.option('--bind-ip', required=True, help='IP Address to bind daemon')
@click.option('--bind-port', required=True, type=int, help='Port to bind daemon')
@with_appcontext
def main(bind_ip, bind_port):
    settings = Provider().settings()
    forward_dns_enabled = settings.get('forward_dns_enabled', False, type=bool)
    forward_dns_address = settings.get('forward_dns_address', [], type=list)
    dns_cache_enabled = settings.get('dns_cache_enabled', False, type=bool)
    dns_cache_max_items = settings.get('dns_cache_max_items', 0, type=int)

    csv_location = ''
    if settings.get('csv_logging_enabled', False, type=bool):
        csv_location = settings.get('csv_logging_file', '', type=str)

    from app.lib.daemon.cli import DNSDaemonCLI
    cli = DNSDaemonCLI()
    return cli.daemon(bind_ip, bind_port, forward_dns_enabled, forward_dns_address, csv_location, dns_cache_enabled, dns_cache_max_items)


@click.command('snitch_start', help='SnitchDNS Start Daemon')
@with_appcontext
def snitch_start():
    provider = Provider()
    daemon = provider.daemon()

    if not daemon.is_configured():
        print("SnitchDNS Daemon is not configured - aborting.")
        return False

    print("SnitchDNS - Starting daemon...")
    return daemon.start()
