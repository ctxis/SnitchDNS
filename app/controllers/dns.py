from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain

bp = Blueprint('dns', __name__, url_prefix='/dns')


@bp.route('/', methods=['GET'])
@login_required
@must_have_base_domain
def index():
    provider = Provider()
    zones = provider.dns_zones()

    # Admins should see global domains (user_id = 0)
    user_id = 0 if current_user.admin else current_user.id

    return render_template(
        'dns/index.html',
        zones=zones.get_user_zones(user_id)
    )


@bp.route('/<int:dns_zone_id>/view', methods=['GET'])
@login_required
@must_have_base_domain
def zone_view(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    return render_template(
        'dns/zone/view.html',
        zone=zone,
        records=records.get_zone_records(dns_zone_id, order_column='type')
    )


@bp.route('/<int:dns_zone_id>/edit', methods=['GET'])
@login_required
@must_have_base_domain
def zone_edit(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

    zone = None
    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    if dns_zone_id > 0:
        if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

        zone = zones.get(dns_zone_id)
        if not zone:
            flash('Zone not found', 'error')
            return redirect(url_for('home.index'))

    return render_template(
        'dns/zone/edit.html',
        dns_zone_id=dns_zone_id,
        user_domain=zones.get_user_base_domain(current_user.username),
        zone=zone
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
@must_have_base_domain
def zone_edit_save(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    if dns_zone_id > 0:
        if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    domain = request.form['domain'].strip() if 'domain' in request.form else ''
    active = True if int(request.form.get('active', 0)) == 1 else False
    exact_match = True if int(request.form.get('exact_match', 0)) == 1 else False
    master = False

    if len(domain) == 0 and 'domain' in request.form:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    base_domain = '' if current_user.admin else zones.get_user_base_domain(current_user.username)
    if zones.has_duplicate(dns_zone_id, domain, base_domain):
        flash('This domain already exists.', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    if dns_zone_id > 0:
        zone = zones.get(dns_zone_id)
        if not zone:
            flash('Could not get zone', 'error')
            return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

        # Now check if it's a master zone and check if there's been an attempt to change the master domain.
        if zone.master:
            if len(domain) > 0 and domain != zone.domain and current_user.admin is False:
                flash('You cannot edit the domain of the master zone.', 'error')
                return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

            domain = zone.domain
            base_domain = zone.base_domain
            master = True
    else:
        zone = zones.create()

    # If it's an admin, create it as a global domain.
    user_id = 0 if current_user.admin else current_user.id
    zone = zones.save(zone, user_id, domain, base_domain, active, exact_match, master)
    if not zone:
        flash('Could not save zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


@bp.route('/<int:dns_zone_id>/record/<int:dns_record_id>/edit', methods=['GET'])
@login_required
@must_have_base_domain
def record_edit(dns_zone_id, dns_record_id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))
    elif dns_record_id > 0:
        if not records.can_access(dns_zone_id, dns_record_id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    record = records.get(dns_record_id, zone.id)
    if dns_record_id > 0:
        if not record:
            flash('Could not load record', 'error')
            return redirect(url_for('home.index'))

    dns_types = records.get_types()
    dns_classes = records.get_classes()

    return render_template(
        'dns/record/edit.html',
        dns_record_id=dns_record_id,
        dns_types=dns_types,
        dns_classes=dns_classes,
        zone=zone,
        record=record
    )


@bp.route('/<int:dns_zone_id>/record/<int:dns_record_id>/edit/save', methods=['POST'])
@login_required
@must_have_base_domain
def record_edit_save(dns_zone_id, dns_record_id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))
    elif dns_record_id > 0:
        if not records.can_access(dns_zone_id, dns_record_id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    dns_types = records.get_types()
    dns_classes = records.get_classes()

    ttl = int(request.form['ttl'].strip())
    rclass = request.form['class'].strip()
    type = request.form['type'].strip()
    active = True if int(request.form.get('active', 0)) == 1 else False

    if ttl <= 0:
        flash('Invalid TTL value', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))
    elif rclass not in dns_classes:
        flash('Invalid class value', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))
    elif type not in dns_types:
        flash('Invalid type value', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))

    # Depending on the type, get the right properties.
    data = gather_record_data(type)
    if data is False:
        # Flash errors should already be set in gather_record_data()
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))

    if dns_record_id > 0:
        record = records.get(dns_record_id, zone.id)
        if not record:
            flash('Could not get record', 'error')
            return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))
    else:
        record = records.create()

    if not records.save(record, zone.id, ttl, rclass, type, data, active):
        flash('Could not save record', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))

    flash('Record saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=dns_zone_id))


def gather_record_data(record_type):
    data = {}
    properties = {}
    if record_type in ['NS', 'CNAME', 'PTR', 'DNAME']:
        properties = {
            'name': 'str'
        }
    elif record_type in ['A', 'AAAA']:
        properties = {
            'address': 'str'
        }
    elif record_type in ['SOA']:
        properties = {
            'mname': 'str',
            'rname': 'str',
            'serial': 'int',
            'refresh': 'int',
            'retry': 'int',
            'expire': 'int',
            'minimum': 'int'
        }
    elif record_type in ['SRV']:
        properties = {
            'target': 'str',
            'port': 'int',
            'priority': 'int',
            'weight': 'int'
        }
    elif record_type in ['NAPTR']:
        properties = {
            'order': 'int',
            'preference': 'int',
            'flags': 'str',
            'service': 'str',
            'regexp': 'str',
            'replacement': 'str'
        }
    elif record_type in ['AFSDB']:
        properties = {
            'hostname': 'str',
            'subtype': 'int'
        }
    elif record_type in ['RP']:
        properties = {
            'mbox': 'str',
            'txt': 'str'
        }
    elif record_type in ['HINFO']:
        properties = {
            'cpu': 'str',
            'os': 'str'
        }
    elif record_type in ['MX']:
        properties = {
            'name2': 'str',
            'preference2': 'int'
        }
    elif record_type in ['SSHFP']:
        properties = {
            'algorithm': 'int',
            'fingerprint_type': 'int',
            'fingerprint': 'str'
        }
    elif record_type in ['TXT', 'SPF']:
        properties = {
            'data': 'str'
        }
    elif record_type in ['TSIG']:
        properties = {
            'algorithm2': 'int',
            'timesigned': 'int',
            'fudge': 'int',
            'original_id': 'int',
            'mac': 'str',
            'other_data': 'str'
        }

    for property, type in properties.items():
        value = request.form[property].strip()
        if type == 'int':
            value = int(value)

        if (type == 'str') and (len(value) == 0):
            flash('Invalid {0} value'.format(property), 'error')
            return False
        elif (type == 'int') and (value < 0):
            flash('Invalid {0} value'.format(property), 'error')
            return False

        if property in ['name2', 'preference2', 'algorithm2']:
            # There are multiple form fields like 'name', 'name2', 'name3',
            # it's easier to clean them up this way than use duplicate names.
            property = property.rstrip('2')
        data[property] = value

    return data
