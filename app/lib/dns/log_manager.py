from sqlalchemy import desc
from app.lib.models.dns import DNSQueryLogModel, DNSZoneModel, DNSRecordModel
from app.lib.dns.instances.query_log import DNSQueryLog


class DNSLogManager:
    def create(self):
        item = DNSQueryLog(DNSQueryLogModel())
        item.save()
        return item

    def __load(self, item):
        return DNSQueryLog(item)

    def get_user_logs(self, user_id):
        query = DNSQueryLogModel.query
        query = query.join(DNSZoneModel, DNSZoneModel.id == DNSQueryLogModel.dns_zone_id)
        query = query.outerjoin(DNSRecordModel, DNSRecordModel.id == DNSQueryLogModel.dns_record_id)
        query = query.filter(DNSZoneModel.user_id == user_id)
        query = query.add_columns(
            DNSQueryLogModel.id,
            DNSQueryLogModel.source_ip,
            DNSQueryLogModel.domain,
            DNSQueryLogModel.rclass,
            DNSQueryLogModel.type,
            DNSQueryLogModel.data,
            DNSQueryLogModel.found,
            DNSZoneModel.full_domain
        )
        query = query.order_by(desc(DNSQueryLogModel.id))

        results = query.all()
        return results

    def get_unmatched_logs(self):
        query = DNSQueryLogModel.query
        # query = query.join(DNSZoneModel, DNSZoneModel.id == DNSQueryLogModel.dns_zone_id)
        query = query.outerjoin(DNSRecordModel, DNSRecordModel.id == DNSQueryLogModel.dns_record_id)
        query = query.filter(DNSQueryLogModel.found == 0)
        query = query.add_columns(
            DNSQueryLogModel.id,
            DNSQueryLogModel.source_ip,
            DNSQueryLogModel.domain,
            DNSQueryLogModel.rclass,
            DNSQueryLogModel.type,
            DNSQueryLogModel.data,
            DNSQueryLogModel.found
        )
        query = query.order_by(desc(DNSQueryLogModel.id))

        results = query.all()
        return results
