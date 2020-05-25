import ldap3


class LDAPManager:
    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, value):
        self.__enabled = value

    @property
    def ssl(self):
        return self.__ssl

    @ssl.setter
    def ssl(self, value):
        self.__ssl = value

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, value):
        self.__host = value

    @property
    def base_dn(self):
        return self.__base_dn

    @base_dn.setter
    def base_dn(self, value):
        self.__base_dn = value

    @property
    def domain(self):
        return self.__domain

    @domain.setter
    def domain(self, value):
        self.__domain = value

    @property
    def bind_user(self):
        return self.__bind_user

    @bind_user.setter
    def bind_user(self, value):
        self.__bind_user = value

    @property
    def bind_pass(self):
        return self.__bind_pass

    @bind_pass.setter
    def bind_pass(self, value):
        self.__bind_pass = value

    @property
    def mapping_username(self):
        return self.__mapping_username

    @mapping_username.setter
    def mapping_username(self, value):
        self.__mapping_username = value

    @property
    def mapping_fullname(self):
        return self.__mapping_fullname

    @mapping_fullname.setter
    def mapping_fullname(self, value):
        self.__mapping_fullname = value

    @property
    def mapping_email(self):
        return self.__mapping_email

    @mapping_email.setter
    def mapping_email(self, value):
        self.__mapping_email = value

    def __init__(self):
        self.__enabled = False
        self.__host = ''
        self.__base_dn = ''
        self.__domain = ''
        self.__bind_user = ''
        self.__bind_pass = ''
        self.__mapping_username = ''
        self.__mapping_fullname = ''
        self.__mapping_email = ''
        self.__ssl = False

    def authenticate(self, username, password):
        connection = self.__connect(username, password)
        if connection:
            # Authentication worked - close connection.
            connection.unbind()

            # Reconnect using the BindUser and return the user's data.
            return self.__load_user(username)
        return False

    def __connect(self, username, password):
        server = ldap3.Server(self.host, get_info=ldap3.ALL, use_ssl=self.ssl)
        ldap_user = "{0}\\{1}".format(self.domain, username)
        connection = ldap3.Connection(server, user=ldap_user, password=password, authentication=ldap3.NTLM)
        result = connection.bind()
        return connection if result else False

    def __load_user(self, username):
        connection = self.__connect(self.bind_user, self.bind_pass)
        if not connection:
            return False

        # Get the mandatory fields first.
        attributes = [self.mapping_username, self.__mapping_fullname]

        # Now the optional fields.
        if len(self.mapping_email) > 0:
            attributes.append(self.mapping_email)

        search = "(&(objectclass=person)({0}={1}))".format(self.mapping_username, username)
        connection.search(self.base_dn, search, attributes=attributes)
        if len(connection.entries) != 1:
            # We're only looking for one record - anything else is an error and it shouldn't have reached this point.
            return False

        return {
            'username': connection.entries[0][self.mapping_username].value,
            'fullname': connection.entries[0][self.mapping_fullname].value,
            'email': connection.entries[0][self.mapping_email].value if len(self.mapping_email) > 0 else ''
        }
