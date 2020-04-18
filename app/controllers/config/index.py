from . import bp
from flask_login import login_required
from flask import redirect, url_for


@bp.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('config.forwarding'))



# from flask import Blueprint
# from flask_login import current_user, login_required
# from flask import render_template, redirect, url_for, flash, request
# from app.lib.base.provider import Provider
#
# bp = Blueprint('config', __name__, url_prefix='/config')
#
#
# @bp.route('/', methods=['GET'])
# @login_required
# def index():
#     return render_template('config/index.html')
#
#
# @bp.route('/save', methods=['POST'])
# @login_required
# def save():
#     provider = Provider()
#     settings = provider.settings()
#     dns = provider.dns()
#
#     forward_dns_address = request.form['forward_dns_address'].strip()
#     forward_dns_enabled = True if int(request.form.get('forward_dns_enabled', 0)) == 1 else False
#
#     forwarders = []
#     for item in forward_dns_address.split(','):
#         item = item.strip()
#         if len(item) > 0:
#             if dns.is_valid_ip_address(item):
#                 forwarders.append(item)
#
#     settings.save_list('forward_dns_address', forwarders)
#     settings.save('forward_dns_enabled', forward_dns_enabled)
#
#     flash('Settings saved', 'success')
#     return redirect(url_for('config.index'))
