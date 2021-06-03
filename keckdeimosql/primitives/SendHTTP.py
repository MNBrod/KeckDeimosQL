"""
author: MBrodheim
"""

import os
import requests
import time

from keckdrpframework.primitives.base_primitive import BasePrimitive

class SendHTTP(BasePrimitive):
    """
    Sends an HTTP GET request to the url in the config file in compliance with
    the RTI API.
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.pipeline_logger
    
    def _pre_condition(self):
        self.user = self.config.params.rti_user
        self.pw = self.config.params.rti_pass
        if self.user == '' or self.pw == '':
            self.logger.error("Username or password is not set for RTI access")
            return False
        return True

    def _perform(self):

        if not self.action.args.koaid:
            self.logger.error(f"Encountered a file with no KOA ID: {self.action.args.name}")
            return self.action.args
        
        data_directory = os.path.join(self.config.params.cwd,
                                      self.config.params.output_directory)
        
        self.logger.info(f"Alerting RTI that {self.action.args.name} is ready for ingestion")

        url = self.config.params.rti_url
        data = {
            'instrument': 'DEIMOS',
            'koaid': self.action.args.koaid,
            'ingesttype': self.config.params.rti_ingesttype,
            'datadir': str(data_directory),
            'start': str(self.action.args.ingest_time),
            'reingest': self.config.params.rti_reingest,
            'testonly': self.config.params.rti_testonly,
            'dev': self.config.params.rti_dev
        }
        
        attempts = 0
        limit = self.config.params.rti_attempts
        while attempts < limit:
            res = self.get_url(url, data)
            if res is None:
                t = self.config.params.rti_retry_time
                attempts += 1
                self.logger.error(f"Waiting {t} seconds to attempt again... ({attempts}/{limit})")
                time.sleep(t)
            else:
                self.logger.info(f"Post returned status code {res.status_code}")
                return self.action.args
        
        self.logger.error(f"Post attempted {limit} times and got no response.")
        self.logger.error("Aborting.")
        return self.action.args
    
    def get_url(self, url, data):
        try:
            res = requests.get(url, params = data, auth=(
                                                        self.user,
                                                        self.pw
                                                        ))
            self.logger.info(f"Sending {res.request.url}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error caught while posting to {url}:")
            self.logger.error(e)
            return None
        return res
