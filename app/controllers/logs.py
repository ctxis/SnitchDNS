from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request, send_file
from app.lib.base.provider import Provider
import time

bp = Blueprint('logs', __name__, url_prefix='/logs')


@bp.route('/', methods=['GET'])
@login_required
def index():
    provider = Provider()
    search = provider.search()

    results = search.search_from_request(request)

    return render_template(
        'logs/index.html',
        results=results['results'],
        params=results['params'],
        filters=results['filters'],
        page_url='logs.index'
    )


@bp.route('/export', methods=['POST'])
@login_required
def export():
    provider = Provider()
    search = provider.search()
    logs = provider.dns_logs()
    users = provider.users()

    # Prepare names and variables.
    filename = str(int(time.time())) + '.csv'
    download_filename = "snitch_logs_" + filename
    save_results_as = users.get_user_data_path(current_user.id, filename=filename)

    # Perform the search.
    results = search.search_from_request(request, paginate=False, method='post')
    rows = results['results']

    # Export to disk.
    if not logs.save_results_csv(rows, save_results_as, overwrite=True):
        flash('Could not generate CSV file.', 'error')
        return redirect(url_for('logs.index'))

    # And download.
    return send_file(save_results_as, attachment_filename=download_filename, as_attachment=True)
