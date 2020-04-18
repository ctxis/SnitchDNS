from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider

bp = Blueprint('dns', __name__, url_prefix='/dns')


@bp.route('/', methods=['GET'])
@login_required
def index():
    provider = Provider()
    dns = provider.dns()

    return render_template(
        'dns/index.html',
        zones=dns.get_all_zones()
    )


@bp.route('/<int:dns_zone_id>/edit', methods=['GET'])
@login_required
def edit(dns_zone_id):
    provider = Provider()
    dns = provider.dns()

    return render_template(
        'dns/edit.html',
        is_edit=(dns_zone_id > 0),
        dns_zone_id=dns_zone_id,
        dns_classes=dns.get_classes(),
        dns_types=dns.get_types(),
        zone=dns.get_zone(dns_zone_id)
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
def edit_save(dns_zone_id):
    provider = Provider()
    dns = provider.dns()

    dns_classes = dns.get_classes()
    dns_types = dns.get_types()

    domain = request.form['domain'].strip()
    ttl = int(request.form['ttl'].strip())
    rclass = request.form['class'].strip()
    type = request.form['type'].strip()
    address = request.form['address'].strip()

    if len(domain) == 0:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    elif ttl < 0:
        flash('Invalid TTL value', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    elif rclass not in dns_classes:
        flash('Invalid class value', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    elif type not in dns_types:
        flash('Invalid type value', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    elif not dns.is_valid_ip_address(address):
        flash('Invalid IP address value', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))

    if dns_zone_id > 0:
        zone = dns.get_zone(dns_zone_id)
        if not zone:
            flash('Could not get zone', 'error')
            return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    else:
        zone = dns.create_zone()

    if not dns.save(zone, domain, ttl, rclass, type, address):
        flash('Could not save zone', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.index'))
