#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 08:34:28 2020

@author: oliver
"""

import os
import requests
import json
import time
from pprint import pprint
from dotenv import load_dotenv
from random import randint
from base64 import b64encode



class AgeAPI:
    """ This is an example of how to hit Inverite API.
    The code is not production ready
    Use it for development
    """
    
    def __init__(self, auth, email, referenceid, siteID, firstname, lastname,
                 ip='127.0.0.1'):
        # this is for sandbox
        self.header = {
            'Accept': 'application/json',
            'Content-type': 'application/json',
            'Auth': auth
        }
        
        self.api_base = "https://sandbox.inverite.com/api/v2/"
        self.siteID = siteID
        
        self.email = email
        self.referenceid = referenceid
        
        self.ip = ip
        
        self.firstname = firstname
        self.lastname = lastname
        
        self.responses = {}  # key by api name
        
    def run(self):
        """ Main entrypoint for iframe url """
        self.create_api()
        print(self.responses['create_api']['iframeurl'])
        time.sleep(10)
        self.check_status()
        self.fetch_api()        
    
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
        url = self.api_base+"create"
        data = {"ip": self.ip,
                "email": self.email,
                "firstname": self.firstname,
                "lastname": self.lastname,
                "siteID": self.siteID,
                "referenceid": self.referenceid,
                "type": "web",
                }
        self.send_request(url, 'create_api', 'POST', data)
        
    def status_api(self):
        url = self.api_base+"status"
        data = {'type':'guid',
                'guid': [self.responses['create_api']['request_guid']]}
        self.send_request(url, 'status_api', 'POST', data)
        
    def check_status(self):
        self.status_api()
        
        while self.responses['status_api']['status'][0]['result'] == 'Not Started':
            time.sleep(5)
            self.status_api()
            
    def fetch_api(self):
        url = self.api_base+'fetch/'+self.responses['create_api']['request_guid']
        self.send_request(url, 'fetch_api')
        
    # below is to use advance api to do everything
    def advance_run(self, files):
        """ Main entrypoint for advanced API """
        self.create_api()
        
        self.advance_fileupload_and_check_status(files)
        self.advance_session_start_api()
        self.advance_check_status()
        
    def advance_upload_image_api(self, filepath, filetype):
        url = self.api_base+"image_upload/"

        data={'guid': self.responses['create_api']['request_guid'],
             'type': filetype,
             'data': b64encode(open(filepath, 'rb').read()).decode('utf-8')
        }
        self.send_request(url, 'image_upload_'+filetype, 'POST', data)
        
    def advance_image_status(self, filetype):
        url = self.api_base+"image_status/"+self.responses["image_upload_"+filetype]['task_id']+f"/{filetype}"
        self.send_request(url, "image_status_"+filetype)
        
    def advance_fileupload_and_check_status(self, files):
        """Helper method
        files is list of tuples (data_type, file_path)
        expect following format 
        
        files = [
            ("face", "path_to_face.jpg"),
            ("front", 'path_to_front_id.jpg'),
            ("rear", "path_to_rear_id.jpg"),
        ]
        """
        
        for ftype, fpath in files:
            self.advance_upload_image_api(fpath, ftype)
            for i in range(100):
                self.advance_image_status(ftype)
                if self.responses["image_status_"+ftype].get('status') == "pending":
                    time.sleep(5)
                else:
                    # make sure it uploaded successfuly
                    break
            else:
                # maxed out
                print("Maxed out image status")
                raise ValueError
                
    def advance_session_start_api(self):
        url = self.api_base+"session_start_av/"+self.responses['create_api']['request_guid']
        self.send_request(url, 'session_start_api')
        
    def advance_session_status_api(self):
        url = self.api_base+"session_status_av/"+self.responses['session_start_api']['task_id']
        self.send_request(url, "session_status_api")
        
    def advance_check_status(self):
        self.advance_session_status_api()
        
        while self.responses['session_status_api']['status'] == 'pending':
            time.sleep(5)
            self.advance_session_status_api()
            
if __name__ == "__main__":
    # example of how this works
    load_dotenv()
    
    kwargs = {
        'auth': os.environ['INVERITE_API_KEY'],
        'siteID': os.environ['INVERITE_AGE_SITE_ID'],
        'referenceid': randint(1000,9999),
        'email': f"test{randint(1000,9999)}@inverite.com",
        'firstname': 'Test',
        'lastname': 'Account',
    }

        
    age = AgeAPI(**kwargs)
    age.run()
    # age.advance_run(files)