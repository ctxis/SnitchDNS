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
    dns = provider.dns()

    # Admins should see global domains (user_id = 0)
    user_id = 0 if current_user.admin else current_user.id

    return render_template(
        'dns/index.html',
        zones=dns.get_user_zones(user_id)
    )


@bp.route('/<int:dns_zone_id>/edit', methods=['GET'])
@login_required
@must_have_base_domain
def edit(dns_zone_id):
    provider = Provider()
    dns = provider.dns()

    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    if dns_zone_id > 0:
        if not dns.can_access_zone(dns_zone_id, current_user.id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    return render_template(
        'dns/edit.html',
        dns_zone_id=dns_zone_id,
        user_domain=dns.get_user_base_domain(current_user.username),
        dns_classes=dns.get_classes(),
        dns_types=dns.get_types(),
        zone=dns.get_zone(dns_zone_id)
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
@must_have_base_domain
def edit_save(dns_zone_id):
    provider = Provider()
    dns = provider.dns()

    dns_zone_id = 0 if dns_zone_id < 0 else dns_zone_id
    if dns_zone_id > 0:
        if not dns.can_access_zone(dns_zone_id, current_user.id, is_admin=current_user.admin):
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

    dns_classes = dns.get_classes()
    dns_types = dns.get_types()

    domain = request.form['domain'].strip()
    ttl = int(request.form['ttl'].strip())
    rclass = request.form['class'].strip()
    type = request.form['type'].strip()
    address = request.form['address'].strip()
    active = True if int(request.form.get('active', 0)) == 1 else False
    exact_match = True if int(request.form.get('exact_match', 0)) == 1 else False

    if len(domain) == 0:
        flash('Invalid domain', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    elif ttl <= 0:
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

    base_domain = '.' if current_user.admin else dns.get_user_base_domain(current_user.username)
    if dns.duplicate_domain_exists(dns_zone_id, domain, base_domain):
        flash('This domain already exists.', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))

    if dns_zone_id > 0:
        zone = dns.get_zone(dns_zone_id)
        if not zone:
            flash('Could not get zone', 'error')
            return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))
    else:
        zone = dns.create_zone()

    # If it's an admin, create it as a global domain.
    user_id = 0 if current_user.admin else current_user.id
    if not dns.save(user_id, zone, domain, base_domain, ttl, rclass, type, address, active, exact_match):
        flash('Could not save zone', 'error')
        return redirect(url_for('dns.edit', dns_zone_id=dns_zone_id))

    flash('Zone saved', 'success')
    return redirect(url_for('dns.index'))


# @bp.route('/logs', methods=['GET'])
# @login_required
# def logs():
#     provider = Provider()
#     dns = provider.dns()
#
#     logs = dns.get_all_logs()
#     filters = dns.get_log_filters()
#
#     return render_template(
#         'dns/logs.html',
#         logs=logs,
#         filters=filters
#     )
