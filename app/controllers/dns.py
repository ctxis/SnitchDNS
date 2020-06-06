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

    return render_template(
        'dns/index.html',
        zones=zones.get_user_zones(current_user.id)
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

    domain = request.form['domain'].strip() if 'domain' in request.form else ''
    active = True if int(request.form.get('active', 0)) == 1 else False
    exact_match = True if int(request.form.get('exact_match', 0)) == 1 else False

    if len(domain) == 0 and 'domain' in request.form:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    if dns_zone_id > 0:
        if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    base_domain = '' if current_user.admin else zones.get_user_base_domain(current_user.username)
    if zones.has_duplicate(dns_zone_id, domain, base_domain):
        flash('This domain already exists.', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    zone = zones.get(dns_zone_id) if dns_zone_id > 0 else zones.create()
    if not zone:
        flash('Could not get zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    # You can't change the domain is this is a master domain.
    master = False
    if zone.master:
        domain = zone.domain
        base_domain = zone.base_domain
        master = True

    zone = zones.save(zone, current_user.id, domain, base_domain, active, exact_match, master)
    if not zone:
        flash('Could not save zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


@bp.route('/<int:dns_zone_id>/delete', methods=['POST'])
@login_required
@must_have_base_domain
def zone_delete(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

    if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    # Not using the instance's .delete() attribute because we first need to delete all child records.
    if not zones.delete(dns_zone_id):
        flash('Could not delete zone', 'error')
        return redirect(url_for('home.index'))

    flash('Zone deleted', 'success')
    return redirect(url_for('home.index'))


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
    cls = request.form['class'].strip()
    type = request.form['type'].strip()
    active = True if int(request.form.get('active', 0)) == 1 else False

    if ttl <= 0:
        flash('Invalid TTL value', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))
    elif cls not in dns_classes:
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

    if not records.save(record, zone.id, ttl, cls, type, data, active):
        flash('Could not save record', 'error')
        return redirect(url_for('dns.record_edit', dns_zone_id=dns_zone_id, dns_record_id=dns_record_id))

    flash('Record saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=dns_zone_id))


@bp.route('/<int:dns_zone_id>/record/<int:dns_record_id>/delete', methods=['POST'])
@login_required
@must_have_base_domain
def record_delete(dns_zone_id, dns_record_id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if not zones.can_access(dns_zone_id, current_user.id, is_admin=current_user.admin):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    record = records.get(dns_record_id, dns_zone_id=zone.id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))
    elif not record:
        flash('Record not found', 'error')
        return redirect(url_for('home.index'))

    record.delete()
    flash('Record deleted', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=dns_zone_id))


def gather_record_data(record_type):
    provider = Provider()
    records = provider.dns_records()

    data = {}
    properties = records.get_record_type_properties(record_type)

    for property, type in properties.items():
        value = request.form[property].strip()
        if type == 'int':
            if not value.isdigit():
                flash('Invalid {0} value'.format(property), 'error')
                return False
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
