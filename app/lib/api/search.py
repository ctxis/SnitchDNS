from app.lib.base.provider import Provider
from app.lib.api.base import ApiBase
from app.lib.api.definitions.search import Search
from app.lib.api.definitions.search_result import SearchResult


class ApiSearch(ApiBase):
    def search(self):
        data = {}
        filters = ['domain', 'source_ip', 'type', 'class', 'matched', 'forwarded', 'blocked', 'user_id', 'tags',
                   'alias', 'date_from', 'time_from', 'date_to', 'time_to', 'page', 'per_page']
        for filter in filters:
            value = self.get_request_param(filter)
            if value:
                data[filter] = value

        results = Provider().search().search_from_request(data, method='dict')

        search = Search()
        search.page = results['results'].page
        search.pages = results['results'].pages
        search.count = results['results'].total

        for result in results['results'].items:
            search_result = SearchResult()
            search_result.id = result.id
            search_result.domain = result.domain
            search_result.source_ip = result.source_ip
            search_result.type = result.type
            search_result.matched = result.found
            search_result.forwarded = result.forwarded
            search_result.blocked = result.blocked
            search_result.date = result.created_at.strftime('%Y-%m-%d %H:%M:%S')
            search_result.zone_id = result.dns_zone_id
            search_result.record_id = result.dns_record_id

            search.results.append(search_result)

        return self.send_valid_response(search)
