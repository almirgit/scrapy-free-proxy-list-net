import scrapy

from free_proxy_list_net.items import FreeProxyListNetItem


class ProxyListSpider(scrapy.Spider):
    name = 'proxy_list'
    allowed_domains = ['free-proxy-list.net']
    start_urls = ['https://free-proxy-list.net/']

    def parse(self, response):
        for row in response.xpath("//table[contains(@class, 'table')]/tbody/tr"):
            columns = row.xpath('td/text()').extract()
            item = FreeProxyListNetItem()
            try:
                item['ip_address'] = columns[0]
                item['port'] = columns[1]
                item['country'] = columns[3]
                item['anonymity'] = columns[4]
                if len(columns) == 8:
                    item['last_checked'] = columns[7]
                else:
                    item['last_checked'] = columns[6]
            except IndexError:
                self.logger.error('IndexError: list index out of range: {}'.format(columns))

            yield item
            #yield {'ip_address': columns[0]}
        
