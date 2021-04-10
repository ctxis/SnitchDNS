from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request, send_file
from app.lib.base.provider import Provider


@bp.route('/', methods=['GET'])
@login_required
def index():
    results_per_page = 20

    provider = Provider()
    zones = provider.dns_zones()
    tags = provider.tags()

    search = request.args.get('search', '').strip()
    search_tags = request.args.getlist('tags')

    page = int(request.args.get('page', 1))
    if page <= 0:
        page = 1

    user_id = None if current_user.admin else current_user.id

    page_url = 'tags=' + '&tags='.join(search_tags)
    page_url += "&search={0}&page=".format(search)

    return render_template(
        'dns/zones/index.html',
        zones=zones.get_user_zones_paginated(user_id, order_by='domain', page=page, per_page=results_per_page, search=search, tags=search_tags),
        page=page,
        per_page=results_per_page,
        page_url=page_url,
        search=search,
        search_tags=search_tags,
        tags=tags.all(user_id=user_id, order_by='asc', order_column='name')
    )


@bp.route('/<int:dns_zone_id>/view', methods=['GET'])
@login_required
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
def zone_edit(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    tags = provider.tags()

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

    user_id = zone.user_id if dns_zone_id > 0 else current_user.id

    return render_template(
        'dns/zones/edit.html',
        dns_zone_id=dns_zone_id,
        user_domain=zones.get_user_base_domain(username),
        zone=zone,
        tags=tags.all(user_id=user_id, order_column='name', order_by='asc')
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
def zone_edit_save(dns_zone_id):
    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    return __zone_create() if dns_zone_id == 0 else __zone_update(dns_zone_id)


@bp.route('/<int:dns_zone_id>/delete', methods=['POST'])
@login_required
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


@bp.route('/delete', methods=['POST'])
@login_required
def zone_group_delete():
    provider = Provider()
    zones = provider.dns_zones()

    search = request.form['search'].strip()
    search_tags = request.form['tags'].strip().split(',')

    zones.group_delete(current_user.id, search=search, tags=search_tags)

    flash('Zone(s) deleted', 'success')
    return redirect(url_for('dns.index'))


def __zone_create():
    provider = Provider()
    zones = provider.dns_zones()
    dns_zone_id = 0

    domain = request.form['domain'].strip().lower()
    active = True if int(request.form.get('active', 0)) == 1 else False
    catch_all = True if int(request.form.get('catch_all', 0)) == 1 else False
    forwarding = True if int(request.form.get('forwarding', 0)) == 1 else False
    regex = True if int(request.form.get('regex', 0)) == 1 else False
    tags = request.form.getlist('tags')

    zone = zones.new(domain, active, catch_all, forwarding, regex, current_user.id, update_old_logs=True)
    if isinstance(zone, list):
        for error in zone:
            flash(error, 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    zone = zones.save_tags(zone, tags)
    if not zone:
        flash('Could not save zone tags', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone created', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


def __zone_update(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Could not get zone', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    domain = request.form['domain'].strip().lower() if not zone.master else zone.domain
    active = True if int(request.form.get('active', 0)) == 1 else False
    catch_all = True if int(request.form.get('catch_all', 0)) == 1 else False
    forwarding = True if int(request.form.get('forwarding', 0)) == 1 else False
    regex = True if int(request.form.get('regex', 0)) == 1 else False
    tags = request.form.getlist('tags')

    if len(domain) == 0:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    if zones.has_duplicate(dns_zone_id, domain):
        flash('This domain already exists.', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    zone = zones.update(zone.id, domain, active, catch_all, forwarding, regex, zone.user_id, master=zone.master, update_old_logs=True)
    if isinstance(zone, list):
        for error in zone:
            flash(error, 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    zone = zones.save_tags(zone, tags)
    if not zone:
        flash('Could not save zone tags', 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


@bp.route('/create/log/<int:query_log_id>', methods=['POST'])
@login_required
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

    zone = zones.new(log.domain, True, False, False, current_user.id, update_old_logs=True)
    if isinstance(zone, list):
        for error in zone:
            flash(error, 'error')
        return redirect(url_for('dns.zone_edit', dns_zone_id=0))

    flash('Zone created', 'success')
    return redirect(url_for('dns.zone_view', dns_zone_id=zone.id))


@bp.route('/export', methods=['POST'])
@login_required
def zones_export():
    provider = Provider()
    zones = provider.dns_zones()

    search = request.form['search'].strip()
    search_tags = request.form['tags'].strip().split(',')

    result = zones.export(user_id=current_user.id, export_zones=True, export_records=True, compress_export=True, search=search, tags=search_tags)
    if not result:
        flash('Could not generate export file.', 'error')
        return redirect(url_for('dns.index'))

    # And download.
    return send_file(result['zip'], attachment_filename='snitch_export.zip', as_attachment=True)
