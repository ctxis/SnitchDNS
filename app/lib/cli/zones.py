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

    headers = ['id', 'user', 'domain', 'active', 'catch-all', 'forwarding', 'regex', 'tags']
    table = []
    for result in results:
        table.append([
            result.id,
            result.user_id,
            result.domain,
            result.active,
            result.catch_all,
            result.forwarding,
            result.regex,
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
@click.option('--catch_all', is_flag=True, help='Domain will be catch-all')
@click.option('--forwarding', is_flag=True, help='Unmatched records will be forwarded (if forwarding is enabled)')
@click.option('--regex', is_flag=True, help='Domain will be evaluated as a regular expression')
@with_appcontext
def cli_zones_add(domain, user_id, active, catch_all, forwarding, regex):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.new(domain, active, catch_all, forwarding, regex, user_id)
    if isinstance(zone, list):
        for error in zone:
            print(error)
        return False

    print("Zone created")
    return True


@main.command('update')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--active', required=False, default=None, help='Domain will be active', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--catch_all', required=False, default=None, help='Domain will be catch-all', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--forwarding', required=False, default=None, help='Unmatched records will be forwarded (if forwarding is enabled)', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--regex', required=False, default=None, help='Domain will be evaluated as a regular expression', type=click.Choice(['yes', 'no', 'true', 'false']))
@with_appcontext
def cli_zones_update(domain, active, catch_all, forwarding, regex):
    provider = Provider()
    zones = provider.dns_zones()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    if active is not None:
        zone.active = (active in ['yes', 'true'])

    if catch_all is not None:
        zone.catch_all = (catch_all in ['yes', 'true'])

    if forwarding is not None:
        zone.forwarding = (forwarding in ['yes', 'true'])

    if regex is not None:
        zone.regex = (regex in ['yes', 'true'])

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


@main.command('import')
@click.option('--file', required=True, help='CSV file to import', type=click.STRING)
@click.option('--user_id', required=True, help='User ID to import zones for', type=click.INT)
@with_appcontext
def cli_zones_import(file, user_id):
    provider = Provider()
    import_manager = provider.dns_import()
    users = provider.users()

    user = users.get_user(user_id)
    if not user:
        print("Could not find user with ID: {0}".format(user_id))
        return False

    import_type = import_manager.identify(file)
    if import_type != import_manager.IMPORT_TYPE_ZONE:
        print("Invalid import file: {0}".format(import_manager.last_error))
        return False

    data = import_manager.review(file, import_type, user.id, show_progressbar=True)
    if not data:
        print("Could not load file: {0}".format(import_manager.last_error))
        return False

    if len(data['errors']) > 0:
        errors = []
        for error in data['errors']:
            errors.append([error['row'], error['error']])
        print(tabulate.tabulate(errors, ['row', 'error']))
        return False

    result = import_manager.run(data['data'], import_type, user.id, show_progressbar=True)
    if result:
        return True

    for error in result:
        print(error)

    return False
