from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain


@bp.route('/aliases', methods=['GET'])
@login_required
@must_have_base_domain
def alias_index():
    provider = Provider()
    aliases = provider.aliases()

    user_id = None if current_user.admin else current_user.id

    return render_template(
        'dns/aliases/index.html',
        aliases=aliases.all(user_id=user_id, order_column='name', order_by='asc')
    )


@bp.route('/aliases/<int:alias_id>/delete', methods=['POST'])
@login_required
@must_have_base_domain
def alias_delete(alias_id):
    provider = Provider()
    aliases = provider.aliases()

    user_id = None if current_user.admin else current_user.id
    if not aliases.can_access(alias_id, user_id):
        flash('You cannot access the selected alias', 'error')
        return redirect(url_for('dns.alias_index'))

    if not aliases.delete(alias_id, user_id=user_id):
        flash('Could not delete alias', 'error')
        return redirect(url_for('dns.alias_index'))

    flash('Alias deleted', 'success')
    return redirect(url_for('dns.alias_index'))


@bp.route('/aliases/<int:alias_id>/edit', methods=['GET'])
@login_required
@must_have_base_domain
def alias_edit(alias_id):
    provider = Provider()
    aliases = provider.aliases()

    user_id = None if current_user.admin else current_user.id
    if alias_id > 0:
        if not aliases.can_access(alias_id, user_id):
            flash('You cannot access the selected alias', 'error')
            return redirect(url_for('dns.alias_index'))

        alias = aliases.get(alias_id, user_id=user_id)
    else:
        alias = None

    return render_template(
        'dns/aliases/edit.html',
        alias_id=alias_id,
        alias=alias
    )


@bp.route('/aliases/<int:alias_id>/edit/save', methods=['POST'])
@login_required
@must_have_base_domain
def alias_edit_save(alias_id):
    provider = Provider()
    aliases = provider.aliases()

    ip = request.form['ip'].strip()
    name = request.form['name'].strip()
    if len(name) == 0:
        flash('Please enter an alias name', 'error')
        return redirect(url_for('dns.alias_index'))
    elif not aliases.is_valid_ip_or_range(ip):
        flash('Please enter a valid IP address', 'error')
        return redirect(url_for('dns.alias_index'))

    alias_with_same_ip = aliases.get(None, user_id=current_user.id, ip=ip)
    if alias_with_same_ip and alias_with_same_ip.id != alias_id:
        flash('An alias with this IP address already exists', 'error')
        return redirect(url_for('dns.alias_index'))

    user_id = None if current_user.admin else current_user.id
    if alias_id > 0:
        if not aliases.can_access(alias_id, user_id):
            flash('You cannot access the selected alias', 'error')
            return redirect(url_for('dns.alias_index'))

        alias = aliases.update(alias_id, ip=ip, name=name)
    else:
        alias = aliases.save(current_user.id, ip, name)

    flash('Alias Created' if alias_id == 0 else 'Alias Updated', 'success')
    return redirect(url_for('dns.alias_index'))
