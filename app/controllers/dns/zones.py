from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain


@bp.route('/', methods=['GET'])
@bp.route('/<string:type>', methods=['GET'])
@login_required
@must_have_base_domain
def index(type=''):
    provider = Provider()
    zones = provider.dns_zones()

    user_id = current_user.id
    if len(type) > 0:
        if current_user.admin and (type == 'all'):
            # This means all domains.
            user_id = None
        else:
            # Return user to the previous page.
            return redirect(url_for('dns.index'))

    return render_template(
        'dns/zones/index.html',
        zones=zones.get_user_zones(user_id, order_by='user_id'),
        type=type
    )


@bp.route('/<int:dns_zone_id>/view', methods=['GET'])
@login_required
@must_have_base_domain
def zone_view(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    records = provider.dns_records()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    return render_template(
        'dns/zones/view.html',
        zone=zone,
        records=records.get_zone_records(dns_zone_id, order_column='type'),
        section='records',
        tab='records'
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
        if not zones.can_access(dns_zone_id, current_user.id):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

        zone = zones.get(dns_zone_id)
        if not zone:
            flash('Zone not found', 'error')
            return redirect(url_for('home.index'))

    username = current_user.username if zone is None else zone.username

    return render_template(
        'dns/zones/edit.html',
        dns_zone_id=dns_zone_id,
        user_domain=zones.get_user_base_domain(username),
        zone=zone
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
@must_have_base_domain
def zone_edit_save(dns_zone_id):
    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    return __zone_create() if dns_zone_id == 0 else __zone_update(dns_zone_id)


@bp.route('/<int:dns_zone_id>/delete', methods=['POST'])
@login_required
@must_have_base_domain
def zone_delete(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Could not get zone', 'error')
        return redirect(url_for('dns.index'))
    elif zone.master:
        flash('You cannot delete a master zone', 'error')
        return redirect(url_for('dns.index'))

    # Not using the instance's .delete() attribute because we first need to delete all child records.
    if not zones.delete(dns_zone_id):
        flash('Could not delete zone', 'error')
        return redirect(url_for('dns.index'))

    flash('Zone deleted', 'success')
    return redirect(url_for('dns.index'))


def __zone_create():
    provider = Provider()
    zones = provider.dns_zones()
    dns_zone_id = 0

    domain = request.form['domain'].strip().lower()
    active = True if int(request.form.get('active', 0)) == 1 else False
    exact_match = True if int(request.form.get('exact_match', 0)) == 1 else False
    forwarding = True if int(request.form.get('forwarding', 0)) == 1 else False

    zone = zones.new(domain, active, exact_match, forwarding, current_user.id)
    if isinstance(zone, list):
        for error in zone:
            flash(error, 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone created', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


def __zone_update(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    users = provider.users()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Could not get zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    if zone.master:
        domain = zone.domain
        base_domain = zone.base_domain
        master = True
    else:
        domain = request.form['domain'].strip().lower()
        base_domain = '' if users.is_admin(zone.user_id) else zones.get_user_base_domain(zone.username)
        master = False

    active = True if int(request.form.get('active', 0)) == 1 else False
    exact_match = True if int(request.form.get('exact_match', 0)) == 1 else False
    forwarding = True if int(request.form.get('forwarding', 0)) == 1 else False

    if len(domain) == 0:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    if zones.has_duplicate(dns_zone_id, domain, base_domain):
        flash('This domain already exists.', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    zone = zones.save(zone, zone.user_id, domain, base_domain, active, exact_match, master, forwarding)
    if not zone:
        flash('Could not save zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


@bp.route('/create/log/<int:query_log_id>', methods=['POST'])
@login_required
@must_have_base_domain
def zone_create_from_log(query_log_id):
    provider = Provider()
    logging = provider.dns_logs()
    zones = provider.dns_zones()

    log = logging.get(query_log_id)
    if not log:
        flash('Could not retrieve log record', 'error')
        return redirect(url_for('home.index'))

    if log.dns_zone_id > 0:
        # This means that the zone exists.
        if not zones.can_access(log.dns_zone_id, current_user.id):
            # This error is misleading on purpose to prevent zone enumeration. Not that it's important by meh.
            flash('Could not retrieve log record', 'error')
            return redirect(url_for('home.index'))

        flash('Zone already exists', 'error')
        return redirect(url_for('dns.zone_view', dns_zone_id=log.dns_zone_id))

    zone = zones.new(log.domain, True, True, False, current_user.id)
    if isinstance(zone, list):
        for error in zone:
            flash(error, 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=0))

    flash('Zone created', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))
