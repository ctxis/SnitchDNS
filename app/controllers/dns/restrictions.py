from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain


@bp.route('/<int:dns_zone_id>/restrictions', methods=['GET'])
@login_required
@must_have_base_domain
def zone_restrictions(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()

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
        section='restrictions',
        tab='restrictions'
    )


@bp.route('/<int:dns_zone_id>/restrictions/<int:restriction_id>/edit', methods=['GET'])
@login_required
@must_have_base_domain
def zone_restrictions_edit(dns_zone_id, restriction_id):
    provider = Provider()
    zones = provider.dns_zones()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    restriction = zone.restrictions.get(restriction_id) if restriction_id > 0 else None

    return render_template(
        'dns/zones/view.html',
        zone=zone,
        section='restrictions_edit',
        tab='restrictions',
        restriction_id=restriction_id,
        restriction=restriction
    )


@bp.route('/<int:dns_zone_id>/restrictions/<int:restriction_id>/edit', methods=['POST'])
@login_required
@must_have_base_domain
def zone_restrictions_edit_save(dns_zone_id, restriction_id):
    provider = Provider()
    zones = provider.dns_zones()
    restrictions = provider.dns_restrictions()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    ip_range = request.form['ip_range'].strip()
    type = int(request.form['type'].strip())
    enabled = True if int(request.form.get('enabled', 0)) == 1 else False

    if len(ip_range) == 0 or not restrictions.is_valid_ip_or_range(ip_range):
        flash('Invalid IP/Range', 'error')
        return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))
    elif type not in [1, 2]:
        flash('Invalid type', 'error')
        return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))

    restriction = restrictions.create(zone_id=zone.id) if restriction_id == 0 else zone.restrictions.get(restriction_id)
    if not restriction:
        flash('Could not load restriction', 'error')
        return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))

    restrictions.save(restriction, zone.id, ip_range, type, enabled)

    flash('Restriction saved', 'success')
    return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))


@bp.route('/<int:dns_zone_id>/restrictions/<int:restriction_id>/delete', methods=['POST'])
@login_required
@must_have_base_domain
def zone_restrictions_delete(dns_zone_id, restriction_id):
    provider = Provider()
    zones = provider.dns_zones()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    restriction = zone.restrictions.get(restriction_id)
    if not restriction:
        flash('Could not get restriction', 'error')
        return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))

    restriction.delete()

    flash('Restriction deleted', 'success')
    return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))


@bp.route('/block/log/<int:query_log_id>', methods=['POST'])
@login_required
@must_have_base_domain
def zone_restriction_create_from_log(query_log_id):
    provider = Provider()
    logging = provider.dns_logs()
    zones = provider.dns_zones()
    restrictions = provider.dns_restrictions()

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

        zone = zones.get(log.dns_zone_id)
        if not zone:
            flash('Could not load zone', 'error')
            return redirect(url_for('home.index'))
    else:
        # There's a chance that the dns_zone_id equals to zero but the domain exists. This can happen if the zone was
        # created from the log files, as the IDs aren't updated after a domain is created (after it's been logged).
        zone = zones.find(log.domain, user_id=current_user.id)
        if not zone:
            # If we still can't find it, create it.
            zone = zones.new(log.domain, True, True, False, current_user.id)
            if isinstance(zone, list):
                for error in zone:
                    flash(error, 'error')
                return redirect(url_for('home.index'))

    # One last check as it may have been loaded by domain.
    if not zones.can_access(zone.id, current_user.id):
        # This error is misleading on purpose to prevent zone enumeration. Not that it's important by meh.
        flash('Could not retrieve log record', 'error')
        return redirect(url_for('home.index'))

    # At this point we should have a valid zone object. First check if the restriction exists.
    restriction = restrictions.find(zone_id=zone.id, ip_range=log.source_ip, type=2)
    if not restriction:
        # Doesn't exist - create it.
        restriction = restrictions.create(zone_id=zone.id)

    # Now update and save.
    restriction = restrictions.save(restriction, zone.id, log.source_ip, 2, True)

    flash('Restriction rule created', 'success')
    return redirect(url_for('dns.zone_restrictions', dns_zone_id=zone.id))
