from sqlalchemy import and_, func, desc
from app.lib.dns.instances.search_params import SearchParams
from app import db
from app.lib.models.dns import DNSQueryLogModel, DNSZoneModel
from flask_login import current_user
import datetime


class SearchManager:
    def search_from_request(self, request, paginate=True, method='get'):
        params = SearchParams(request=request, method=method)
        return {
            'results': self.search(params, paginate=paginate),
            'params': params,
            'filters': self.get_filters()
        }

    def search(self, search_params, paginate=False):
        query = DNSQueryLogModel.query

        # Default is that users can only search for themselves.
        user_ids = [current_user.id]
        if current_user.admin:
            # Plot-twist! Unless they are an admin.
            if search_params.user_id == 0:
                # Search for everyone.
                user_ids = []
            elif search_params.user_id > 0:
                user_ids = [search_params.user_id]

        if len(user_ids) > 0:
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

        if len(search_params.cls) > 0:
            query = query.filter(DNSQueryLogModel.cls == search_params.cls)

        if len(search_params.type) > 0:
            query = query.filter(DNSQueryLogModel.type == search_params.type)

        if search_params.matched in [0, 1]:
            query = query.filter(DNSQueryLogModel.found == bool(search_params.matched))

        if search_params.forwarded in [0, 1]:
            query = query.filter(DNSQueryLogModel.forwarded == bool(search_params.forwarded))

        if search_params.blocked in [0, 1]:
            query = query.filter(DNSQueryLogModel.blocked == bool(search_params.blocked))

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
            'types': [],
            'users': {}
        }

        sql = "SELECT cls FROM dns_query_log GROUP BY cls ORDER BY cls"
        results = db.session.execute(sql)
        for result in results:
            filters['classes'].append(result.cls)

        sql = "SELECT type FROM dns_query_log GROUP BY type ORDER BY type"
        results = db.session.execute(sql)
        for result in results:
            filters['types'].append(result.type)

        sql = "SELECT id, username FROM users GROUP BY id, username ORDER BY username"
        results = db.session.execute(sql)
        for result in results:
            filters['users'][result.id] = result.username

        return filters
