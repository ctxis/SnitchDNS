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

    @property
    def master(self):
        return self.item.master

    @master.setter
    def master(self, value):
        self.item.master = value

    def build_zone(self, record, domain=None):
        domain = self.domain if domain is None else domain
        zone_items = [
            str(domain),
            str(record.ttl),
            str(record.rclass),
            str(record.type),
            str(record.data)
        ]

        return "\t".join(zone_items)

    @property
    def full_domain(self):
        return self.item.full_domain

    @full_domain.setter
    def full_domain(self, value):
        self.item.full_domain = value
