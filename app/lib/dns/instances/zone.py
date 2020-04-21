from app.lib.dns.base_instance import BaseDNSInstance


class DNSZone(BaseDNSInstance):
    @property
    def domain(self):
        return self.item.domain

    @domain.setter
    def domain(self, value):
        self.item.domain = value

    @property
    def base_domain(self):
        return self.item.base_domain

    @base_domain.setter
    def base_domain(self, value):
        self.item.base_domain = value

    @property
    def ttl(self):
        return self.item.ttl

    @ttl.setter
    def ttl(self, value):
        self.item.ttl = value

    @property
    def rclass(self):
        return self.item.rclass

    @rclass.setter
    def rclass(self, value):
        self.item.rclass = value

    @property
    def type(self):
        return self.item.type

    @type.setter
    def type(self, value):
        self.item.type = value

    @property
    def address(self):
        return self.item.address

    @address.setter
    def address(self, value):
        self.item.address = value

    @property
    def active(self):
        return self.item.active

    @active.setter
    def active(self, value):
        self.item.active = value

    @property
    def exact_match(self):
        return self.item.exact_match

    @exact_match.setter
    def exact_match(self, value):
        self.item.exact_match = value

    @property
    def user_id(self):
        return self.item.user_id

    @user_id.setter
    def user_id(self, value):
        self.item.user_id = value

    def build_zone(self, domain=None):
        domain = self.domain if domain is None else domain
        zone_items = [
            str(domain),
            str(self.ttl),
            str(self.rclass),
            str(self.type),
            str(self.address)
        ]

        return "\t".join(zone_items)
