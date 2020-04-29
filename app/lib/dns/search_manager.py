from app.lib.dns.instances.search_params import SearchParams
from app.lib.dns.instances.search_result import SearchResult
from app import db
import datetime


class SearchManager:
    def search_from_request(self, request):
        params = SearchParams(request)
        return {
            'results': self.search(params),
            'params': params,
            'filters': self.get_filters()
        }

    def search(self, search_params):
        where = []
        params = {}

        sql = '''
            SELECT *
            FROM dns_query_log ql
            WHERE 
        '''

        if len(search_params.domain) > 0:
            operator = 'LIKE' if '%' in search_params.domain else '='
            where.append("ql.domain {0} :domain".format(operator))
            params['domain'] = search_params.domain

        if len(search_params.source_ip) > 0:
            operator = 'LIKE' if '%' in search_params.source_ip else '='
            where.append("ql.source_ip {0} :source_ip".format(operator))
            params['source_ip'] = search_params.source_ip

        if len(search_params.rclass) > 0:
            where.append("ql.rclass = :rclass")
            params['rclass'] = search_params.rclass

        if len(search_params.type) > 0:
            where.append("ql.type = :type")
            params['type'] = search_params.type

        if search_params.matched in [0, 1]:
            where.append("ql.found = :found")
            params['found'] = search_params.matched

        if search_params.forwarded in [0, 1]:
            where.append("ql.forwarded = :forwarded")
            params['forwarded'] = search_params.forwarded

        date_from = search_params.full_date_from
        date_to = search_params.full_date_to
        if isinstance(date_from, datetime.datetime):
            where.append("ql.created_at >= :date_from")
            params['date_from'] = date_from.strftime('%Y-%m-%d %H:%M:%S')

        if isinstance(date_to, datetime.datetime):
            where.append("ql.created_at <= :date_to")
            params['date_to'] = date_to.strftime('%Y-%m-%d %H:%M:%S')

        if len(where) > 0:
            where = " AND ".join(where)
            sql = sql + where
        else:
            sql = sql + " 1=1 "

        results = db.session.execute(sql, params)
        output = []
        for result in results:
            output.append(SearchResult(result))

        return output

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
