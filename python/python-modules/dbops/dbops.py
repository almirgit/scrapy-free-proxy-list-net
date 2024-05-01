import logging
lg = logging.getLogger(__name__)

import psycopg2
import sys
import time


class CustomException(Exception):
    pass

class CustomExceptionDataNotFound(Exception):
    pass

class DB:
    def __init__(self, conn_params):
        self._conn_params = conn_params
        self.conn = None
        self.cursor = None

    def open_connection(self):
        if not self.conn:
            while True:
                try:
                    self._connect_str = "dbname='{}' user='{}' host='{}' password='{}' sslmode=disable".format(
                        self._conn_params['pgdb_name'],
                        self._conn_params['pgdb_user'],
                        self._conn_params['pgdb_host'],
                        self._conn_params['pgdb_pass'],
                        )
                    self.conn = psycopg2.connect(self._connect_str)
                    #self.open_cursor()
                    lg.debug("DB connection open")
                    return
                except Exception:
                    e = sys.exc_info()
                    lg.error("Exception: {}. Sleeping for 5 seconds...".format(e))
                    time.sleep(5)
        else:
            lg.debug("No need to open DB connection")

    def close_connection(self):
        try:
            self.conn.close()
            lg.debug("DB connection closed")
        except:
            lg.debug("No need to close DB connection")

    def transaction_commit(self, log=True):
        self.conn.commit()
        if log:
            lg.debug("DB commit")

    def open_cursor(self):
        try:
            self.cursor = self.conn.cursor()
            lg.debug("DB open cursor")
        except Exception as e:
            lg.debug("No need to open DB cursor")

    def close_cursor(self):
        pass
        #try:
        #    self.cursor.close()
        #    lg.debug("DB close cursor")
        #except:
        #    lg.debug("No need to close DB cursor")


    def execute_sql(self, sql, input_params):
        retry = True
        while retry:
            try:
                self.open_connection()
                self.open_cursor()
                lg.debug(f"Executing '{sql}' using parameters:" + str(input_params))
                self.cursor.execute(sql, input_params)
                self.transaction_commit()
                retry = False
            except Exception as e:
                # Not sure what Exception is called so here goes workaround:
                if "cursor already closed" in str(e):
                    lg.warning('"cursor already closed" occured. Opening new cursor, sleep 2 seconds and retry...')
                    self.open_cursor()
                    time.sleep(2)
                else:
                    lg.error(f"Error executing '{sql}' using parameters:" + str(input_params) + '; ' + str(e))


    # Get config value:
    def get_config(self, config_name, 
            app_scheme='app', 
            config_table='config',
            default_value=None, 
            raise_error=None):
        self.open_connection()
        self.open_cursor()
        try:
            sql = f"""select value from {app_scheme}.{config_table} where name = %s"""
            self.cursor.execute(sql, (config_name, ))
            fetchone = self.cursor.fetchone()
            if not fetchone:
                if raise_error:
                    raise CustomException(f'Error fetching configuragion value: {config_name}')
            if fetchone:
                sys.stdout.write("Debug: For value '{}' fetched '{}' from DB\n".format(config_name, fetchone[0]))
                sys.stdout.flush()
                return fetchone[0]
            return default_value
        #except NoneType: # TODO: how to catch NoneType??
        #    sys.stderr.write(f'Error fetching config: {config_name}: Not found\n')
        except Exception as e:
            lg.error(str(e))
            if raise_error:
                raise CustomException(f'Error fetching configuragion value: {config_name}')
            else:
                sys.stderr.write(f'Error fetching configuragion value: {config_name}. Return default...\n')
                sys.stderr.flush()
                return default_value
        finally:
            pass
            #self.close_cursor()


    def get_scalar(self, sql, args_tuple):
        fname = 'dbops.get_scalar'
        self.open_connection()
        self.open_cursor()
        try:
            self.cursor.execute(sql, args_tuple)
            #self.transaction_commit()
            fetchone = self.cursor.fetchone()
            return fetchone[0]
        except TypeError as e:
            errmsg = fname + ": No data found while executing sql '{}' with parameters '{}'".format(sql, str(args_tuple))
            #sys.stderr.write(errmsg + "\n")
            #sys.stderr.flush()
            #return None
            raise CustomExceptionDataNotFound(errmsg)
        except Exception as e:
            errmsg = fname + ": DB query error: " + str(e) + '\n'
            #sys.stderr.write(fname + ": DB query error: " + str(e) + '\n')
            #sys.stderr.flush()
            return CustomExceptionDataNotFound(errmsg)
        finally:
            # db.close_cursor() # Causes 'Error registring node: cursor already closed.' ??
            pass

        
    def get_vector(self, sql, args_tuple=None):
        fname = 'dbops.get_vector'
        self.open_connection()
        self.open_cursor()
        try:
            if args_tuple:
                self.cursor.execute(sql, args_tuple)
            else:
                self.cursor.execute(sql)
            #self.transaction_commit()
            res = self.cursor.fetchall()
            return res
        except TypeError as e:
            errmsg = fname + ": No data found while executing sql '{}' with parameters '{}'".format(sql, str(args_tuple))
            raise CustomExceptionDataNotFound(errmsg)
        except Exception as e:
            errmsg = fname + ": DB query error: " + str(e) + '\n'
            return CustomExceptionDataNotFound(errmsg)
        finally:
            # db.close_cursor() # Causes 'Error registring node: cursor already closed.' ??
            pass


    def dbwrite(self, sql, args_tuple):
        fname = 'dbops.dbwrite'
        self.open_connection()
        self.open_cursor()
        try:
            #print("===> About to write: " + str(args_tuple))
            self.cursor.execute(sql, args_tuple)
            self.transaction_commit()
        #except TypeError as e:
        #    errmsg = fname + ": No data found while executing sql '{}' with parameters '{}'".format(sql, str(args_tuple))
        #    raise CustomExceptionDataNotFound(errmsg)
        except Exception as e:
            errmsg = fname + ": DB query error: " + str(e) + '\n'
            return CustomExceptionDataNotFound(errmsg)
        finally:
            # db.close_cursor() # Causes 'Error registring node: cursor already closed.' ??
            pass

