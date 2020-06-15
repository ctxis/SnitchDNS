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
