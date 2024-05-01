import logging
lg = logging.getLogger(__name__)

import psycopg2
import sys

#class NotFoundError(Exception):
#class CustomException(Exception):
#    pass


from dbops import DB
class DB_Proxy_Load(DB):
    pass

    def get_proxy_list(self, n_records=350):
        try:
            self.open_connection()
            self.open_cursor()
            sql = """select extract(epoch from pl.moddate)::bigint moddate_ts, pl.proxy_ip, pl.proxy_port, pl.moddate, pl.id from data.proxy_list pl order by pl.moddate desc limit %s"""
            #self.cursor.execute(sql, (n_records, ))
            self.execute_sql(sql, (n_records, ))
            result = self.cursor.fetchall()
            self.close_cursor()
            return result
        except Exception as e:
            # Not sure what Exception is called so here goes workaround:
            if "cursor already closed" in str(e):
                #lg.warning('"cursor already closed" occured: {}.'.format(str(e)))
                #lg.warning('"cursor already closed" occured')
                e = sys.exc_info()
                import traceback
                traceback.print_exc()
                return
            #sys.stderr.write('Error fetching proxy_list: {}.\n'.format(str(e)))
            #sys.stderr.flush()
            lg.error('Error fetching proxy_list: {}.'.format(str(e)))
            return None

