from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider

bp = Blueprint('dns', __name__, url_prefix='/dns')


@bp.route('/', methods=['GET'])
@login_required
def index():
    return render_template('dns/index.html')


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
        dns_types=dns.get_types()
    )


@bp.route('/<int:dns_zone_id>/edit/save', methods=['POST'])
@login_required
def edit_save(dns_zone_id):
    return 'yes'
