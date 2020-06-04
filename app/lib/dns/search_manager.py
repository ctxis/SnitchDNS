from sqlalchemy import and_, func, desc
from app.lib.dns.instances.search_params import SearchParams
from app import db
from app.lib.models.dns import DNSQueryLogModel, DNSZoneModel
import datetime


class SearchManager:
    def search_from_request(self, request, paginate=True, method='get', user_ids=None):
        params = SearchParams(request=request, method=method)
        return {
            'results': self.search(params, paginate=paginate, user_ids=user_ids),
            'params': params,
            'filters': self.get_filters()
        }

    def search(self, search_params, paginate=False, user_ids=None):
        query = DNSQueryLogModel.query
        if user_ids is not None:
            if isinstance(user_ids, str) or isinstance(user_ids, int):
                user_ids = [user_ids]

            if isinstance(user_ids, list) and len(user_ids) > 0:
                query = query.outerjoin(DNSZoneModel, DNSZoneModel.id == DNSQueryLogModel.dns_zone_id)
                query = query.filter(DNSZoneModel.user_id.in_(user_ids))

        if len(search_params.domain) > 0:
            if '%' in search_params.domain:
                query = query.filter(DNSQueryLogModel.domain.ilike(search_params.domain))
            else:
                query = query.filter(func.lower(DNSQueryLogModel.domain) == search_params.domain.lower())

        if len(search_params.source_ip) > 0:
            if '%' in search_params.source_ip:
                query = query.filter(DNSQueryLogModel.source_ip.ilike(search_params.source_ip))
            else:
                query = query.filter(DNSQueryLogModel.source_ip == search_params.source_ip)

        if len(search_params.rclass) > 0:
            query = query.filter(DNSQueryLogModel.rclass == search_params.rclass)

        if len(search_params.type) > 0:
            query = query.filter(DNSQueryLogModel.type == search_params.type)

        if search_params.matched in [0, 1]:
            query = query.filter(DNSQueryLogModel.found == search_params.matched)

        if search_params.forwarded in [0, 1]:
            query = query.filter(DNSQueryLogModel.forwarded == search_params.forwarded)

        date_from = search_params.full_date_from
        date_to = search_params.full_date_to
        if isinstance(date_from, datetime.datetime):
            query = query.filter(DNSQueryLogModel.created_at >= date_from)

        if isinstance(date_to, datetime.datetime):
            query = query.filter(DNSQueryLogModel.created_at <= date_to)

        query = query.order_by(desc(DNSQueryLogModel.id))

        if paginate:
            rows = query.paginate(search_params.page, search_params.per_page, False)
        else:
            rows = query.all()
        return rows

    def get_filters(self):
        filters = {
            'classes': [],
            'types': []
        }

        sql = "SELECT rclass FROM dns_query_log GROUP BY rclass ORDER BY rclass"
        results = db.session.execute(sql)
        for result in results:
            filters['classes'].append(result.rclass)

        sql = "SELECT type FROM dns_query_log GROUP BY type ORDER BY type"
        results = db.session.execute(sql)
        for result in results:
            filters['types'].append(result.type)

        return filters
