import click
import tabulate
import os
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

    headers = ['id', 'user', 'domain', 'active', 'exact match', 'forwarding', 'tags']
    table = []
    for result in results:
        table.append([
            result.id,
            result.user_id,
            result.full_domain,
            result.active,
            result.exact_match,
            result.forwarding,
            ', '.join(result.tags)
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


@main.command('export')
@click.option('--output', required=True, help='CSV File', type=click.STRING)
@click.option('--user_id', required=False, default=None, help='User ID to export zones for', type=click.INT)
@click.option('--search', required=False, default=None, help='Filter zones using a search query', type=click.STRING)
@click.option('--tags', required=False, default=None, help='Filter by tags (comma separated)', type=click.STRING)
@click.option('--include-records', is_flag=True, help='If set a second file will be generated that will include the records for the exported domains')
@with_appcontext
def cli_zones_export(output, user_id, search, tags, include_records):
    provider = Provider()
    zones = provider.dns_zones()

    tags = tags.split(',') if tags is not None else None

    result = zones.export(user_id=user_id, search=search, tags=tags, export_zones=True, export_records=include_records)
    if not result:
        print("Could not export data")
        return False

    os.rename(result['zones'], output)
    print("Zone export saved as: {0}".format(output))
    if include_records:
        path = os.path.dirname(output)
        file = os.path.basename(output).split('.')
        if len(file) > 1:
            extension = file[-1]
            del file[-1]
            file.append('records')
            file.append(extension)
        else:
            file.append('records')

        save_records_as = os.path.join(path, '.'.join(file))
        os.rename(result['records'], save_records_as)
        print("Record export saved as: {0}".format(save_records_as))

    return True
