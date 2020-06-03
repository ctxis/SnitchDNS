import click
from app.lib.base.provider import Provider


@click.command('snitch_daemon', help='SnitchDNS Daemon')
@click.option('--bind-ip', required=True, help='IP Address to bind daemon')
@click.option('--bind-port', required=True, type=int, help='Port to bind daemon')
def main(bind_ip, bind_port):
    settings = Provider().settings()
    forward_dns_enabled = int(settings.get('forward_dns_enabled', 0))
    forward_dns_address = settings.get_list('forward_dns_address')

    from app.lib.daemon.cli import DNSDaemonCLI
    cli = DNSDaemonCLI()
    return cli.daemon(bind_ip, bind_port, forward_dns_enabled, forward_dns_address)
