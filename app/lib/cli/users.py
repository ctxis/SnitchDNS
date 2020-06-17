import click
import tabulate
from flask.cli import with_appcontext
from app.lib.base.provider import Provider


@click.group('users', help='SnitchDNS User Management')
@with_appcontext
def main():
    pass


@main.command('list')
@with_appcontext
def cli_users_list():
    provider = Provider()
    users = provider.users()

    results = users.all()

    headers = ['id', 'username', 'full name', 'email', 'admin', 'active', 'ldap', '2fa']
    table = []
    for user in results:
        table.append([
            user.id,
            user.username,
            user.full_name,
            user.email,
            user.admin,
            user.active,
            user.ldap,
            user.has_2fa()
        ])

    print(tabulate.tabulate(table, headers))
    return True


@main.command('add')
@click.option('--username', required=True, help='Username', type=click.STRING)
@click.option('--password', required=False, default='', help='Password - If defined in the CLI it should be a bcrypt hash, otherwise you will be prompted to enter it.', type=click.STRING)
@click.option('--full_name', required=True, help='Full Name', type=click.STRING)
@click.option('--email', required=True, help='E-Mail', type=click.STRING)
@click.option('--active', required=True, help='User will be active', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--admin', required=True, help='User will be an administrator', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--ldap', required=True, help='User will be authenticated against the LDAP server (if configured)', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--create_zone', is_flag=True, help='Whether a master zone fill be created for the user')
@with_appcontext
def cli_users_add(username, password, full_name, email, active, admin, ldap, create_zone):
    provider = Provider()
    users = provider.users()
    zones = provider.dns_zones()

    active = (active in ['true', 'yes'])
    admin = (admin in ['true', 'yes'])
    ldap = (ldap in ['true', 'yes'])

    ask_for_password = False
    if len(password) == 0:
        # If it's an LDAP user, we don't need it.
        if not ldap:
            ask_for_password = True

    if ask_for_password:
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)

    # If the user entered the password manually it's in plaintext so we can check for complexity.
    user = users.save(0, username, password, full_name, email, admin, ldap, active, check_complexity=ask_for_password, hash_password=ask_for_password)
    if not user:
        print(users.last_error)
        return False

    if create_zone:
        if not zones.create_user_base_zone(user):
            print('User has been created but there was a problem creating their base domain. Make sure the DNS Base Domain has been set.')
            return False

    print("User created")
    return True


@main.command('update')
@click.option('--username', required=True, help='Username', type=click.STRING)
@click.option('--update_password', is_flag=True, help='Whether to update the password. This is used in combination with --password.')
@click.option('--password', required=False, default='', help='Password - If defined in the CLI it should be a bcrypt hash, otherwise you will be prompted to enter it.', type=click.STRING)
@click.option('--full_name', required=False, default=None, help='Full Name', type=click.STRING)
@click.option('--email', required=False, default=None, help='E-Mail', type=click.STRING)
@click.option('--active', required=False, default=None, help='User will be active', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--admin', required=False, default=None, help='User will be an administrator', type=click.Choice(['yes', 'no', 'true', 'false']))
@click.option('--ldap', required=False, default=None, help='User will be authenticated against the LDAP server (if configured)', type=click.Choice(['yes', 'no', 'true', 'false']))
@with_appcontext
def cli_users_update(username, password, full_name, email, active, admin, ldap, update_password):
    provider = Provider()
    users = provider.users()

    user = users.find_user_login(username, None)
    if not user:
        print("Could not find user")
        return False

    active = user.active if active is None else (active in ['true', 'yes'])
    admin = user.admin if admin is None else (admin in ['true', 'yes'])
    ldap = user.ldap if ldap is None else (ldap in ['true', 'yes'])

    ask_for_password = False
    hash_password = False
    check_complexity = False
    if update_password:
        if len(password) == 0:
            if not ldap:
                ask_for_password = True
                check_complexity = True
                hash_password = True
        else:
            ask_for_password = False
            hash_password = False
            check_complexity = False
    else:
        password = user.password
        hash_password = False
        check_complexity = False

    if ask_for_password:
        password = click.prompt('Password', hide_input=True, confirmation_prompt=True)

    # If the user entered the password manually it's in plaintext so we can check for complexity.
    user = users.save(user.id, username, password, full_name, email, admin, ldap, active, check_complexity=check_complexity, hash_password=hash_password)
    if not user:
        print(users.last_error)
        return False

    print("User updated")
    return True
