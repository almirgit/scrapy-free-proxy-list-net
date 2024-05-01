#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s:%(lineno)s - %(levelname)s - %(message)s')
lg = logging.getLogger('main')


import argparse
import os
import sys
import time
import yaml

from datetime import datetime

import sentry_sdk

script_dir = os.path.dirname(__file__)

module_dir = os.path.join(script_dir, 'python-modules', 'dbops')
sys.path.append(module_dir)
module_dir = os.path.join(script_dir, 'python-modules', 'dbops_proxy_load')
sys.path.append(module_dir)
module_dir = os.path.join(script_dir, 'python-modules', 'call_subprocess')
sys.path.append(module_dir)

#import mymodule
#mymodule.say_hello()

from call_subprocess import Subprocess
from dbops import DB
from dbops_proxy_load import DB_Proxy_Load

import dbops_proxy_load


def get_utc_datetime():
    dd = datetime.utcnow()
    return dd.strftime("%Y%m%d%H%M%S")


class Params:
    pass


class Main:

    def __init__(self):
        ##BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.BASE_DIR = os.path.dirname(os.path.realpath(__file__))
        self.BASE_DIR = self.BASE_DIR + '/'
        
    def _action(self, par):
        ##ts_suffix = get_utc_datetime()

        lg.debug('Subprocess start')
        lg.debug('BASE_DIR: ' + self.BASE_DIR)
        cs = Subprocess()
        cs.call_scrapy_proxy(self.BASE_DIR + 'free_proxy_list_net', 
                report_dropped=par.report_dropped
                )
        lg.debug('Subprocess end')
        ##time.sleep(2) # Test
        
        proxy_list_rec = par.db.get_proxy_list(par.records_to_export)
        
        if proxy_list_rec:
            proxy_list_file = par.data_dir + '/' + par.proxy_list_file

            with open(proxy_list_file, 'w') as pf:
                for line in proxy_list_rec:
                    pf.write(str(line[0]) + '|' + 
                            str(line[1]) + ':' + 
                            str(line[2]) + '|' + 
                            str(line[3]) + '|' + 
                            str(line[4])                            
                            )
                    pf.write('\n')
            lg.info(f"Proxy list exported to file '{proxy_list_file}'")


    def exit_procedure(self, msg, db=None, exit_code=100):
        lg.error('Error/Exit messge: ' + str(msg))
        try:
            db.close_connection()
            e = sys.exc_info()
            if e != (None, None, None):
                import traceback
                traceback.print_exc()
        except:
            #lg.error('Cannot close DB connection!')
            lg.error('Error in exit_procedure')
            e = sys.exc_info()
            import traceback
            traceback.print_exc()
        exit(exit_code)


    def main(self):
        lg.info('Program Start')
        parser = argparse.ArgumentParser()
        parser.add_argument("-s", "--secret-file", help="Configuration file with secrets", type=str, default='/app-proxy/config/.secret.yml')
        args = parser.parse_args()

        par = Params()

        try:
            conf_file = args.secret_file
            with open(conf_file) as fh:
                par.cfg_secret = yaml.load(fh, Loader=yaml.SafeLoader)
        except IOError:
            lg.error("Cannot open secret configuration file: {}\n".format(conf_file))
            sys.exit(2)

        os_stat = os.stat(args.secret_file)
        fperm_octal = str(oct(os_stat.st_mode)[-3:])
        if fperm_octal not in ['600', '640']:
            lg.error(f"Secret file '{args.secret_file}' too open: mask '{fperm_octal}'. Must be 600.\n")
            sys.exit(2)

        try: 
            par.db=DB_Proxy_Load(par.cfg_secret)
            sentry_dsn = par.db.get_config('sentry_dsn', raise_error=True)
            par.data_dir = par.db.get_config('data_dir', default_value='/app-proxy/data')
        except Exception as ex:
            self.exit_procedure(ex, db=par.db)


        sentry_project = sentry_dsn

        sentry_sdk.init(
            sentry_project,
            environment='staging', # todo: read from .env accessable from docker
            traces_sample_rate=1.0
        )
        
        try:
            mode = 0o755
            #path = os.path.join(parent_dir, directory) 
            os.makedirs(par.data_dir, mode) 
        except FileExistsError:
            pass


        # Main infinite loop:
        lg.info('Loop Start')
        while True:
            try:
                par.report_dropped = par.db.get_config('report_dropped', default_value='No')
                par.proxy_list_file = par.db.get_config('proxy_list_file', default_value='proxy_list.csv')
                par.records_to_export = par.db.get_config('records_to_export', default_value=350)
                
                lg.info('Action Call')
                self._action(par) 
                time.sleep(30*60) # TODO: make this flexible (over DB or something)
                ##time.sleep(20) # Test
            except KeyboardInterrupt:
                self.exit_procedure('Good Bye!', db=par.db)
            except:
                try:
                    e = sys.exc_info()
                    import traceback
                    traceback.print_exc()
                    lg.error(format(e))
                    lg.info("Exception: {}. Sleeping for 15 minutes...".format(e))
                    time.sleep(15*60)
                except KeyboardInterrupt:
                    self.exit_procedure('Good Bye!', db=par.db)

        self.exit_procedure('Good Bye!', db=par.db)


mp = Main()
exit(mp.main())

