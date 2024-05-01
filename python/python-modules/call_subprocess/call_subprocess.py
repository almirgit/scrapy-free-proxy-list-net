
# Version 0.1

import os
import subprocess
import sys

class Subprocess:

    def call_scrapy_proxy(self, scrapy_dir, report_dropped='No'):
        orig_wd = scrapy_dir
        os.chdir(orig_wd)
        #result = subprocess.run(["scrapy", "crawl", 
        subprocess.run(["scrapy", "crawl", 
            "-a", f'report_dropped={report_dropped}',
            #"--logfile", scrapy_log_file, 
            "proxy_list"], 
            # https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
            #stdout=subprocess.PIPE, 
            #stderr=subprocess.PIPE,
            #capture_output=True,
            text=True,
            check=True)
        #sys.stdout.write(result.stdout)
        #sys.stderr.write(result.stderr)
        #sys.stdout.flush()

    def call_scrapy_njuskalo(self, 
            spider, 
            scrapy_dir, 
            ROTATING_PROXY_LIST_PATH, 
            category, 
            expected_pages, 
            ON_ERROR_RETRY_TIMES,
            ON_ERROR_SLEEP_SECS,
            report_dropped='No',
            ):
        orig_wd = scrapy_dir
        os.chdir(orig_wd)
        #print('------------------------------> Debug: call_scrapy_njuskalo: orig_wd: ' + orig_wd)
        #print('------------------------------> Debug: call_scrapy_njuskalo: pwd: ' + os.getcwd())
        subprocess.run(["scrapy", "crawl", 
            "-a", f'report_dropped={report_dropped}',
            "-a", f'category={category}',
            "-a", f'expected_pages={expected_pages}',
            "-s", f'ROTATING_PROXY_LIST_PATH={ROTATING_PROXY_LIST_PATH}',
            "-s", f'ON_ERROR_RETRY_TIMES={ON_ERROR_RETRY_TIMES}',
            "-s", f'ON_ERROR_SLEEP_SECS={ON_ERROR_SLEEP_SECS}',
            spider], 
            text=True,
            check=True)
