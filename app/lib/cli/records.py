import click
import tabulate
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.group('records', help='SnitchDNS Zone Record Management')
@with_appcontext
def main():
    pass


@main.command('list')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@with_appcontext
def cli_records_list(domain):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    results = records.get_zone_records(zone.id, order_column='type')

    headers = ['id', 'ttl', 'class', 'type', 'active', 'data']
    table = []
    for record in results:
        table.append([
            record.id,
            record.ttl,
            record.cls,
            record.type,
            record.active,
            str(record.properties())
        ])

    print(tabulate.tabulate(table, headers))
    return True


@main.command('delete')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--type', required=False, default=None, help='Type of record to delete. If more than one records with the same type exist, both will be deleted', type=click.STRING)
@click.option('--id', required=False, default=None, help='Record ID to delete.', type=click.INT)
@with_appcontext
def cli_records_list(domain, type, id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if type is None and id is None:
        print("At least one of --type and --id has to be used")
        return False

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    results = records.get_zone_records(zone.id, order_column='type')
    record_deleted = False
    for record in results:
        if type is not None:
            if record.type == type.upper():
                record_deleted = True
                records.delete(record)
        elif id is not None:
            if record.id == id:
                record_deleted = True
                records.delete(record)

    message = "Record deleted" if record_deleted else "Record not found"
    print(message)
    return True


@main.command('add')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--type', required=True, help='Record Type', type=click.Choice(['A', 'AAAA', 'AFSDB', 'CNAME', 'DNAME', 'HINFO', 'MX', 'NAPTR', 'NS', 'PTR', 'RP', 'SOA', 'SPF', 'SRV', 'SSHFP', 'TSIG', 'TXT']))
@click.option('--cls', required=False, default='IN', help='Record Class', type=click.Choice(['ANY', 'CH', 'CS', 'HS', 'IN']))
@click.option('--ttl', required=True, help='Record Type', type=click.INT)
@click.option('--active', is_flag=True, help='Record will be active')
@click.option('--property', required=True, multiple=True, type=(str, str))
@with_appcontext
def cli_records_add(domain, type, cls, ttl, active, property):
    # Convert tuple to dict.
    properties = {}
    for p in property:
        properties[p[0]] = p[1]

    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if ttl < 0:
        print("Invalid TTL value")
        return False

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    expected_properties = records.get_record_type_properties(type, clean=True)
    type_data = {}
    for property_name, property_type in expected_properties.items():
        if property_name not in properties:
            print('Missing type property {0}'.format(property_name))
            return False

        value = properties[property_name]
        if (type == 'int') and (isinstance(value, str)):
            if not value.isdigit():
                print('Invalid {0} value'.format(property_name))
                return False
            value = int(value)

        if (type == 'str') and (len(value) == 0):
            print('Invalid {0} value'.format(property_name))
            return False
        elif (type == 'int') and (value < 0):
            print('Invalid {0} value'.format(property_name))
            return False

        type_data[property_name] = value

    record = records.create()
    record = records.save(record, zone.id, ttl, cls, type, type_data, active)

    print("Record created")
    return True


@main.command('update')
@click.option('--domain', required=True, help='Domain', type=click.STRING)
@click.option('--id', required=True, help='Record ID to update.', type=click.INT)
@click.option('--type', required=False, default=None, help='Record Type', type=click.Choice(['A', 'AAAA', 'AFSDB', 'CNAME', 'DNAME', 'HINFO', 'MX', 'NAPTR', 'NS', 'PTR', 'RP', 'SOA', 'SPF', 'SRV', 'SSHFP', 'TSIG', 'TXT']))
@click.option('--cls', required=False, default=None, help='Record Class', type=click.Choice(['ANY', 'CH', 'CS', 'HS', 'IN']))
@click.option('--ttl', required=False, default=None, help='Record Type', type=click.INT)
@click.option('--active', required=False, default=None, help='Record will be active', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--property', required=False, multiple=True, type=(str, str))
@with_appcontext
def cli_records_update(domain, id, type, cls, ttl, active, property):
    # Convert tuple to dict.
    properties = {}
    for p in property:
        properties[p[0]] = p[1]

    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    record = records.get(id)
    if not record:
        print("Record not found")
        return False

    type = record.type if type is None else type
    cls = record.cls if cls is None else cls
    ttl = record.ttl if ttl is None else ttl
    active = record.active if active is None else active in ['true', 'yes']
    data = record.data if len(properties) == 0 else properties

    if ttl < 0:
        print("Invalid TTL value")
        return False

    zone = zones.find(domain)
    if not zone:
        print("Could not find domain")
        return False

    if data != record.data:
        type_properties = record.properties()
        # This means there's come incoming data.
        expected_properties = records.get_record_type_properties(type, clean=True)
        for property_name, property_value in data.items():
            if property_name not in expected_properties:
                print("Unsupported property '{0}' for type '{1}'".format(property_name, type))
                return False

            property_type = expected_properties[property_name]
            if (property_type == 'int') and (isinstance(property_value, str)):
                if not property_value.isdigit():
                    print('Invalid {0} value'.format(property_name))
                    return False
                property_value = int(property_value)

            if (property_type == 'str') and (len(property_value) == 0):
                print('Invalid {0} value'.format(property_name))
                return False
            elif (property_type == 'int') and (property_value < 0):
                print('Invalid {0} value'.format(property_name))
                return False

            type_properties[property_name] = property_value

        data = type_properties

    record = records.save(record, zone.id, ttl, cls, type, data, active)

    print("Record updated")
    return True
