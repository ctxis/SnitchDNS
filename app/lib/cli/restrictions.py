import click
import tabulate
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.group('restrictions', help='SnitchDNS Zone IP Restriction Management')
@with_appcontext
def main():
    pass


@main.command('list')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@with_appcontext
def cli_restrictions_list(domain):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    headers = ['id', 'ip/range', 'type', 'enabled']
    table = []
    for restriction in zone.restrictions.all():
        table.append([
            restriction.id,
            restriction.ip_range,
            'Allow' if restriction.type == 1 else 'Block',
            restriction.enabled
        ])

    print(tabulate.tabulate(table, headers))
    return True


@main.command('delete')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--iprange', required=False, default=None, help='Range to delete. This should match exactly the value stored.', type=click.STRING)
@click.option('--id', required=False, default=None, help='Restriction ID to delete.', type=click.INT)
@with_appcontext
def cli_restrictions_delete(domain, iprange, id):
    provider = Provider()
    zones = provider.dns_zones()

    if iprange is None and id is None:
        print("One of --iprange or --id should be used")
        return False

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    if id is not None:
        restriction = zone.restrictions.get(id)
        if not restriction:
            print("Could not find restriction with id {0}".format(id))
            return False
    elif iprange is not None:
        for restriction in zone.restrictions.all():
            if iprange == 'all':
                restriction.delete()
            elif iprange == restriction.ip_range:
                restriction.delete()

    print("Restriction(s) deleted")
    return True


@main.command('add')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--iprange', required=True, help='Restriction IP or Range. Use 0.0.0.0 to match all addresses', type=click.STRING)
@click.option('--type', required=True, help='Restriction Type', type=click.Choice(['allow', 'block']))
@click.option('--enabled', is_flag=True, help='Restriction will be enabled')
@with_appcontext
def cli_restrictions_add(domain, iprange, type, enabled):
    provider = Provider()
    zones = provider.dns_zones()
    restrictions = provider.dns_restrictions()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    if len(iprange) == 0 or not restrictions.is_valid_ip_or_range(iprange):
        print("Invalid IP Range")
        return False

    type = 1 if type == 'allow' else 2

    restriction = restrictions.create(zone_id=zone.id)
    restrictions.save(restriction, zone.id, iprange, type, enabled)

    print("Restriction created")
    return True


@main.command('update')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--id', required=True, help='Restriction ID to update.', type=click.INT)
@click.option('--iprange', required=False, default=None, help='Restriction IP or Range. Use 0.0.0.0 to match all addresses', type=click.STRING)
@click.option('--type', required=None, default=None, help='Restriction Type', type=click.Choice(['allow', 'block']))
@click.option('--enabled', required=False, default=None, help='Restriction will be enabled', type=click.Choice(['yes', 'no', 'true', 'false']))
@with_appcontext
def cli_restrictions_update(domain, id, iprange, type, enabled):
    provider = Provider()
    zones = provider.dns_zones()
    restrictions = provider.dns_restrictions()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    restriction = zone.restrictions.get(id)
    if not restriction:
        print("Could not find restriction")
        return False

    iprange = restriction.ip_range if iprange is None else iprange
    if len(iprange) == 0 or not restrictions.is_valid_ip_or_range(iprange):
        print("Invalid IP Range")
        return False

    enabled = restriction.enabled if enabled is None else enabled in ['yes', 'true']
    type = restriction.type if type is None else (1 if type == 'allow' else 2)

    restrictions.save(restriction, zone.id, iprange, type, enabled)

    print("Restriction updated")
    return True
