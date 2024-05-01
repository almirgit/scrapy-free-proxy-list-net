# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


import psycopg2
import sys
import time

class FreeProxyListNetPipeline:

    def __init__(self, db_host, db_port, db_name, db_user, db_pass, report_dropped, log=None):
        self.__db_host = db_host
        self.__db_port = db_port
        self.__db_name = db_name
        self.__db_user = db_user
        self.__db_pass = db_pass
        self._report_dropped = report_dropped
        
        #self.log = log
        self.__snapshot_time = time.strftime('%y%m%d') + time.strftime('%H%M%S')

    @staticmethod
    def read_secret_file(conf_file='/app-proxy/config/.secret.yml'):
        try:
            import yaml
            with open(conf_file) as fh:
                cfg_secret = yaml.load(fh, Loader=yaml.SafeLoader)
            return cfg_secret
        except IOError:
            import logging
            logging.error(f"ERROR: Cannot open secret configuration file: {conf_file}\n")
            sys.exit(2)

    @classmethod
    def from_crawler(cls, crawler):
        cfg_secret = cls.read_secret_file()
        return cls(
            db_host=cfg_secret['pgdb_host'],
            db_port=cfg_secret['pgdb_port'],
            db_name=cfg_secret['pgdb_name'],
            db_user=cfg_secret['pgdb_user'],
            db_pass=cfg_secret['pgdb_pass'],
            report_dropped = getattr(crawler.spider, "report_dropped"),
            #log=crawler.log
        )

    def open_spider(self, spider):
        self.__connection = psycopg2.connect("dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(
            self.__db_name, 
            self.__db_user, 
            self.__db_host, 
            self.__db_port, 
            self.__db_pass))
        self.__cursor = self.__connection.cursor()

    def close_spider(self, spider):
        self.__cursor.close()
        self.__connection.commit()
        self.__connection.close()

    def process_item(self, item, spider):
        if item['anonymity'] != 'elite proxy':
            if self._report_dropped == 'Yes':
                raise DropItem("Not an elite proxy: %s" % item)
            else:
                return
            
        #self.__cursor.execute("insert into data.proxy_list (proxy_ip, proxy_port, country, anonymity, last_checked) values(%s, %s, %s, %s, %s)", (
        self.__cursor.execute("select app.add_new_proxy(%s, %s, %s, %s, %s)", (
            item.get('ip_address'), 
            item.get('port'),
            item.get('country'),
            item.get('anonymity'),
            item.get('last_checked'),
            ))
        self.__connection.commit()
        return item


