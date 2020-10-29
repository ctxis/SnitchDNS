from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/tags', methods=['GET'])
@login_required
def tags_index():
    provider = Provider()
    tags = provider.tags()

    user_id = None if current_user.admin else current_user.id

    return render_template(
        'dns/tags/index.html',
        tags=tags.all(user_id=user_id, order_column='name', order_by='asc')
    )


@bp.route('/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def tags_delete(tag_id):
    provider = Provider()
    zones = provider.dns_zones()
    tags = provider.tags()

    user_id = None if current_user.admin else current_user.id
    if not tags.can_access(tag_id, user_id):
        flash('You cannot access the selected tag', 'error')
        return redirect(url_for('dns.tags_index'))

    zones.tag_delete(tag_id)

    if not tags.delete(tag_id, user_id=user_id):
        flash('Could not delete tag', 'error')
        return redirect(url_for('dns.tags_index'))

    flash('Tag deleted', 'success')
    return redirect(url_for('dns.tags_index'))


@bp.route('/tags/<int:tag_id>/edit', methods=['GET'])
@login_required
def tags_edit(tag_id):
    provider = Provider()
    tags = provider.tags()

    user_id = None if current_user.admin else current_user.id
    if tag_id > 0:
        if not tags.can_access(tag_id, user_id):
            flash('You cannot access the selected tag', 'error')
            return redirect(url_for('dns.tags_index'))

        tag = tags.get(tag_id, user_id=user_id)
    else:
        tag = None

    return render_template(
        'dns/tags/edit.html',
        tag_id=tag_id,
        tag=tag
    )


@bp.route('/tags/<int:tag_id>/edit/save', methods=['POST'])
@login_required
def tags_edit_save(tag_id):
    provider = Provider()
    tags = provider.tags()

    name = request.form['name'].strip().lower()
    if len(name) == 0:
        flash('Please enter a tag name', 'error')
        return redirect(url_for('dns.tags_index'))

    user_id = None if current_user.admin else current_user.id
    if tag_id > 0:
        if not tags.can_access(tag_id, user_id):
            flash('You cannot access the selected tag', 'error')
            return redirect(url_for('dns.tags_index'))

        tag = tags.update(tag_id, name)
    else:
        tag = tags.save(current_user.id, name)

    flash('Tag Created' if tag_id == 0 else 'Tag Updated', 'success')
    return redirect(url_for('dns.tags_index'))
