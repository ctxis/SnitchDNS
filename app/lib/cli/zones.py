import click
import tabulate
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.group('zones', help='SnitchDNS Zone Management')
@with_appcontext
def main():
    pass


@main.command('list')
@with_appcontext
def cli_zones_list():
    provider = Provider()
    zones = provider.dns_zones()

    results = zones.all()

    headers = ['id', 'user', 'domain', 'active', 'exact match', 'forwarding']
    table = []
    for result in results:
        table.append([
            result.id,
            result.user_id,
            result.full_domain,
            result.active,
            result.exact_match,
            result.forwarding,
        ])

    print(tabulate.tabulate(table, headers))
    return True


@main.command('delete')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@with_appcontext
def cli_zones_delete(domain):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    zones.delete(zone.id)
    print("Domain {0} deleted".format(domain))
    return True


@main.command('add')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--user_id', required=True, help='User ID to own the domain', type=click.INT)
@click.option('--active', is_flag=True, help='Domain will be active')
@click.option('--exact_match', is_flag=True, help='Domain will have to be exact match to respond to queries')
@click.option('--forwarding', is_flag=True, help='Unmatched records will be forwarded (if forwarding is enabled)')
@with_appcontext
def cli_zones_add(domain, user_id, active, exact_match, forwarding):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.new(domain, active, exact_match, forwarding, user_id)
    if isinstance(zone, list):
        for error in zone:
            print(error)
        return False

    print("Zone created")
    return True


@main.command('update')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--active', required=False, default=None, help='Domain will be active', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--exact_match', required=False, default=None, help='Domain will have to be exact match to respond to queries', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--forwarding', required=False, default=None, help='Unmatched records will be forwarded (if forwarding is enabled)', type=click.Choice(['yes', 'no', 'true', 'false']))
@with_appcontext
def cli_zones_update(domain, active, exact_match, forwarding):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    if active is not None:
        zone.active = (active in ['yes', 'true'])

    if exact_match is not None:
        zone.exact_match = (exact_match in ['yes', 'true'])

    if forwarding is not None:
        zone.forwarding = (forwarding in ['yes', 'true'])

    zone.save()

    print("Zone updated")
    return True
