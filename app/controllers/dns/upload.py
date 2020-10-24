from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request, send_file
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain
import time
import os


@bp.route('/import', methods=['GET'])
@login_required
@must_have_base_domain
def zones_import():
    return render_template(
        'dns/import/index.html'
    )


@bp.route('/import/upload', methods=['POST'])
@login_required
@must_have_base_domain
def zones_import_upload():
    provider = Provider()
    import_manager = provider.dns_import()

    if len(request.files) != 1:
        flash('Uploaded file could not be found', 'error')
        return redirect(url_for('dns.zones_import'))

    file = request.files['csvfile']
    if file.filename == '':
        flash('No file uploaded', 'error')
        return redirect(url_for('dns.zones_import'))

    file.save(import_manager.get_user_data_path(current_user.id, filename='import.csv'))

    return redirect(url_for('dns.zones_import_review'))


@bp.route('/import/upload/review', methods=['GET'])
@login_required
@must_have_base_domain
def zones_import_review():
    provider = Provider()
    import_manager = provider.dns_import()

    file = import_manager.get_user_data_path(current_user.id, filename='import.csv')
    if not os.path.isfile(file):
        flash('No file uploaded', 'error')
        return redirect(url_for('dns.zones_import'))

    import_type = import_manager.identify(file)
    if import_type is False:
        flash("Error: {0}".format(import_manager.last_error), 'error')
        return redirect(url_for('dns.zones_import'))

    data = import_manager.review(file, import_type, current_user.id)
    if not data:
        flash("Error: {0}".format(import_manager.last_error), 'error')
        return redirect(url_for('dns.zones_import'))

    return render_template(
        'dns/import/review.html',
        data=data['data'],
        errors=data['errors'],
        type=import_type
    )


@bp.route('/import/upload/run', methods=['POST'])
@login_required
@must_have_base_domain
def zones_import_run():
    provider = Provider()
    import_manager = provider.dns_import()

    file = import_manager.get_user_data_path(current_user.id, filename='import.csv')
    if not os.path.isfile(file):
        flash('No file uploaded', 'error')
        return redirect(url_for('dns.zones_import'))

    import_type = import_manager.identify(file)
    if import_type is False:
        flash("Error: {0}".format(import_manager.last_error), 'error')
        return redirect(url_for('dns.zones_import'))

    data = import_manager.review(file, import_type, current_user.id)
    if not data:
        flash("Error: {0}".format(import_manager.last_error), 'error')
        return redirect(url_for('dns.zones_import'))
    elif len(data['errors']) > 0:
        flash("Please fix all the uploaded file's errors before importing it", 'error')
        return redirect(url_for('dns.zones_import_review'))

    result = import_manager.run(data['data'], import_type, current_user.id)
    if result is True:
        # Delete file after process.
        os.remove(file)

        flash('Data has been successfully imported', 'success')
        return redirect(url_for('dns.index'))

    for error in result:
        flash(error, 'error')
    return redirect(url_for('dns.zones_import_review'))
