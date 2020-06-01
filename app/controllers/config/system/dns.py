from .. import bp
from flask import request, render_template, flash, redirect, url_for
from flask_login import login_required
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required


@bp.route('/dns', methods=['GET'])
@login_required
@admin_required
def dns():
    return render_template('config/system/dns.html')


@bp.route('/dns/save', methods=['POST'])
@login_required
@admin_required
def dns_save():
    provider = Provider()
    settings = provider.settings()
    dns = provider.dns_manager()

    # DNS Base Domain
    dns_base_domain = request.form['dns_base_domain'].strip()

    # DNS Daemon
    dns_daemon_bind_ip = request.form['dns_daemon_bind_ip'].strip()
    dns_daemon_bind_port = int(request.form['dns_daemon_bind_port'].strip())

    # DNS Forwarding
    forward_dns_address = request.form['forward_dns_address'].strip()
    forward_dns_enabled = True if int(request.form.get('forward_dns_enabled', 0)) == 1 else False

    # DNS Daemon Validation
    if not dns.is_valid_ip_address(dns_daemon_bind_ip):
        flash('Invalid IP Address', 'error')
        return redirect(url_for('config.dns'))
    elif dns_daemon_bind_port <= 0 or dns_daemon_bind_port > 65535:
        flash('Invalid Port', 'error')
        return redirect(url_for('config.dns'))
    elif dns_daemon_bind_port < 1024:
        flash('Please enter a port between 1024 and 65535. Port numbers below 1024 require root access.', 'error')
        return redirect(url_for('config.dns'))

    # DNS Forwarding Validation
    forwarders = []
    for item in forward_dns_address.split(','):
        item = item.strip()
        if len(item) > 0:
            if dns.is_valid_ip_address(item):
                forwarders.append(item)

    # Save Base Domain
    settings.save('dns_base_domain', dns_base_domain)

    # Save Daemon
    settings.save('dns_daemon_bind_ip', dns_daemon_bind_ip)
    settings.save('dns_daemon_bind_port', dns_daemon_bind_port)

    # Save Forwarding
    settings.save_list('forward_dns_address', forwarders)
    settings.save('forward_dns_enabled', forward_dns_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('config.dns'))
