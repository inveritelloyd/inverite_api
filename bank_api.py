"""
Created on Wed Jul  8 09:45:08 2020

@author: oliver
"""


import os
import requests
import json
import time

from random import randint
from dotenv import load_dotenv
from pprint import pprint


class BankAPI:
    """ This is an example of how to hit Inverite API.
    The code is not production ready
    Use it for development
    """
    
    def __init__(self, auth, email, referenceid, siteID, firstname, lastname,
                 bankID, username, password, ip='127.0.0.1'):
        # this is for sandbox
        self.header = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Auth': auth}
        
        self.api_base = "https://sandbox.inverite.com/api/v2/"
        self.siteID = siteID  
        # Test bank
        self.bank_creds = {
            'bankID': bankID,
            'useragent': "Mozilla/etc",
            'username': username,
            'password': password
        }
        
        self.email = email
        self.referenceid = referenceid
        self.ip = ip
        
        self.firstname = firstname
        self.lastname = lastname
        
        self.responses = {}  # key by api name
        
    def run(self):
        """ Main entrypoint to run a bank api to get iframe url """
        self.create_api()
        print(self.responses['create_api']['iframeurl'])
        time.sleep(10)
        self.check_status()
        self.fetch_api()     
        
                
    def run_advance(self):
        """ Main entrypoint for running advanced api """
        self.create_api()
        self.advance_session_start()
        self.advance_check_status()        
        # self.fetch_api()
    
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
        print(res.status_code, "Response:", api_name)
        try:
            json_result = res.json()
        except Exception as e:
            print("EXC in json", res.content)
            raise e
        pprint(json_result)
        self.responses[api_name] = json_result
        
    def list_info(self, option):
        """ list bank or site
        option can be 'banks' 'sites' or 'branches'
        """
        url = self.api_base+"list"
        data = {'type': option}
        self.send_request(url, 'list_api', 'POST', data)

    def create_api(self, force_new_request=0):
        url = self.api_base+"create"
        data = {"ip": self.ip,
                "email": self.email,
                #"email": "wrong",
                "firstname": self.firstname,
                "lastname": self.lastname,
                "siteID": self.siteID,
                "referenceid": self.referenceid,
                "force_new_request": force_new_request,
                "type": "web",
                # "language_pref": "french"
                }
        self.send_request(url, 'create_api', 'POST', data)
        
    def status_api(self):
        url = self.api_base+"status"
        data = {'type':'guid',
                'guid': [self.responses['create_api']['request_guid']]}
        self.send_request(url, 'status_api', 'POST', data)
        
    def check_status(self):
        self.status_api()
        
        while self.responses['status_api']['status'][0]['result'] in ['Not Started', 'Processing']:
            time.sleep(5)
            self.status_api()
            
    def fetch_api(self):
        url = self.api_base+'fetch/'+self.responses['create_api']['request_guid']
        self.send_request(url, 'fetch_api')
        
    # below are advanced APIs
    def advance_session_start(self):
        url = self.api_base+"session_start/"+self.responses['create_api']['request_guid']
        # test bank
        data = self.bank_creds

        self.send_request(url, 'session_start_api', 'POST', data)
        
    def advance_session_status(self):
        url = self.api_base+'session_status/'+self.responses['session_start_api']['job_id']
        self.send_request(url, 'session_status_api')
        
    def advance_session_challenge(self):
        url = self.api_base+'session_challenge_response/'+self.responses['session_start_api']['job_id']
        answer = input(self.responses['session_status_api']['challenge'])
        data = {"response": answer}
        self.send_request(url, 'session_challenge_response_api', 'POST', data)
        
    def advance_check_status(self):
        time.sleep(5)
        self.advance_session_status()

        while self.responses['session_status_api']['status'] in ['working', 'need_input', 'need_dropdown_input']:
            print(self.responses['session_status_api']['status'])
            if self.responses['session_status_api']['status'] in ['need_input', 'need_dropdown_input']:
                self.advance_session_challenge()
            time.sleep(5)
            self.advance_session_status()
    
    def refresh(self):
        """ Used to trigger refresh on the bank request """
        url = self.api_base+'refresh'
        self.send_request(url, 'refresh_api', method='POST',
                          data={'guid': self.responses['create_api']['request_guid']})
        

if __name__ == "__main__":
    # example of how this works
    load_dotenv()
    
    kwargs = {
        'auth': os.environ['INVERITE_API_KEY'],
        'siteID': os.environ['INVERITE_SITE_ID'],
        'referenceid': randint(1000,9999),
        'email': f"test{randint(1000,9999)}@inverite.com",
        'username': 'success',
        'password': 'success',
        'firstname': 'Test',
        'lastname': 'Account',
        'bankID': 117, # 117 for test bank for sandbox
    }
    bank_api = BankAPI(**kwargs)
    
    # bank_api.list_info('sites')
    # bank_api.list_info('banks')
    # bank_api.run()
    bank_api.run_advance()
    # bank_api.refresh()

