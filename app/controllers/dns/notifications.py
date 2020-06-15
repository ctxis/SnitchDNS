from . import bp
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import must_have_base_domain
import re


@bp.route('/<int:dns_zone_id>/notifications', methods=['GET'])
@login_required
@must_have_base_domain
def zone_notifications(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    notifications = provider.notifications()

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
        section='notifications',
        tab='notifications',
        has_enabled_providers=notifications.providers.has_enabled(),
        providers=notifications.providers.get_enabled()
    )


@bp.route('/<int:dns_zone_id>/notifications/save', methods=['POST'])
@login_required
@must_have_base_domain
def zone_notifications_save(dns_zone_id):
    provider = Provider()
    zones = provider.dns_zones()
    logs = provider.dns_logs()
    notifications = provider.notifications()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('home.index'))

    max_id = logs.get_last_log_id(zone.id)
    for type in ['email', 'webpush', 'slack']:
        enabled = True if int(request.form.get(type, 0)) == 1 else False
        notifications.save_zone_subscription(zone.id, type, enabled=enabled, last_query_log_id=max_id)

    flash('Notification preferences saved', 'success')
    return redirect(url_for('dns.zone_notifications', dns_zone_id=dns_zone_id))


@bp.route('/<int:dns_zone_id>/notifications/<string:item>', methods=['GET'])
@login_required
@must_have_base_domain
def zone_notifications_settings(dns_zone_id, item):
    provider = Provider()
    zones = provider.dns_zones()
    notifications = provider.notifications()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('dns.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('dns.index'))

    notification_provider = notifications.providers.get(item)
    if not notification_provider:
        flash('Invalid notification provider', 'error')
        return redirect(url_for('dns.index'))
    elif not notification_provider.enabled:
        flash('Notification provider is not enabled', 'error')
        return redirect(url_for('dns.index'))
    elif not notification_provider.has_settings:
        flash('Notification provider has no settings', 'error')
        return redirect(url_for('dns.index'))

    return render_template(
        'dns/zones/view.html',
        zone=zone,
        tab='notifications',
        section='{0}_settings'.format(item),
        has_enabled_providers=notifications.providers.has_enabled(),
        subscription=zone.notifications.get(item)
    )


@bp.route('/<int:dns_zone_id>/notifications/<string:item>/save', methods=['POST'])
@login_required
@must_have_base_domain
def zone_notifications_settings_save(dns_zone_id, item):
    provider = Provider()
    zones = provider.dns_zones()
    notifications = provider.notifications()

    if not zones.can_access(dns_zone_id, current_user.id):
        flash('Access Denied', 'error')
        return redirect(url_for('dns.index'))

    zone = zones.get(dns_zone_id)
    if not zone:
        flash('Zone not found', 'error')
        return redirect(url_for('dns.index'))

    notification_provider = notifications.providers.get(item)
    if not notification_provider:
        flash('Invalid notification provider', 'error')
        return redirect(url_for('dns.index'))
    elif not notification_provider.enabled:
        flash('Notification provider is not enabled', 'error')
        return redirect(url_for('dns.index'))
    elif not notification_provider.has_settings:
        flash('Notification provider has no settings', 'error')
        return redirect(url_for('dns.index'))

    if item == 'email':
        recipients = request.form.getlist('recipients[]')
        valid_recipients = []
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        for recipient in recipients:
            recipient = recipient.strip().lower()
            if len(recipient) > 0 and email_regex.match(recipient):
                valid_recipients.append(recipient)

        # Remove duplicates.
        valid_recipients = list(dict.fromkeys(valid_recipients))

        subscription = zone.notifications.get(item)
        if subscription:
            subscription.data = valid_recipients
            subscription.save()
    elif item == 'slack':
        slack_webhook_url = request.form['slack_webhook_url'].strip()

        subscription = zone.notifications.get(item)
        if subscription:
            subscription.data = slack_webhook_url
            subscription.save()

    flash('Notification settings saved.')
    return redirect(url_for('dns.zone_notifications_settings', dns_zone_id=dns_zone_id, item=item))
