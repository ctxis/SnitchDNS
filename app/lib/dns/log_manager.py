from app.lib.models.dns import DNSQueryLogModel
from app.lib.dns.instances.query_log import DNSQueryLog


class DNSLogManager:
    def create(self):
        item = DNSQueryLog(DNSQueryLogModel())
        item.save()
        return item
