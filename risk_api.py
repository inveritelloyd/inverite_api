#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 12:55:45 2021

@author: oliver
"""



import os
import requests
import json
import time
from pprint import pprint
from dotenv import load_dotenv



class RiskAPI:
    """ This is an example of how to hit Inverite API.
    The code is not production ready
    Use it for development
    """
    
    def __init__(self, auth, request_guid):
        
        self.header = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Auth': auth
        }
    
        self.api_base = "https://sandbox.inverite.com/api/v2/"
        self.request_guid = request_guid
        
        self.responses = {}  # key by api name
        
    def run(self):
        self.create_api()
        self.check_status()
    
    def send_request(self, url, api_name, method='GET', data={}):
        """Files is more media"""
        if method.lower() == 'get':
            res = requests.get(url, headers=self.header)
        elif method.lower() == 'post':
            res = requests.post(url, headers=self.header, json=data)
        else:
            print("UNRECOGNIZED request method", method)
            return
        print('\n')
        print("Response:", api_name)
        json_result = res.json()
        pprint(json_result)
        self.responses[api_name] = json_result
        
    def create_api(self):
        url = self.api_base+"risk"
        data = {"request": self.request_guid}
        self.send_request(url, 'create_api', 'POST', data)
        
    def check_status(self):
        task_id = self.responses['create_api']['task_id']
        url = self.api_base+"risk_status/"+task_id
        result = "pending"
        while result == "pending":
            time.sleep(5)
            self.send_request(url, 'status_api')
            result = self.responses['status_api']['status']
        print("DONE")
    
if __name__ == "__main__":
    # example of how this works
    load_dotenv()
    
    kwargs = {
        'auth': os.environ['INVERITE_API_KEY'],
        'request_guid': ''  # some successful request guid
    }

    risk = RiskAPI(**kwargs)
    risk.run()