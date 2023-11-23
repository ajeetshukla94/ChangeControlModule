# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 16:22:11 2022


Default users password : P@ssw0rd
"""
import pandas as pd
import datetime
import time
import os
import mysql.connector
from mysql.connector import errorcode
from dateutil.tz import gettz
import os 
import io
from crypt_services import encrypt_sha256
import base64
from base64 import b64encode
from pathlib import Path
MYDIR        = os.path.dirname(__file__)

   
config = {
  'host':"pinpointserver.mysql.database.azure.com",
  'port':"3306",
  'user':"arissdb",
  'password':"ppedbpass@12",
  'db':'ccndb'
}



def convert_into_binary(file_path):
    with open(file_path, 'rb') as file:
        binary=file.read()
    return binary

class DBO:
    def __init__(self):
        try:           
            pass                
        except Exception as e:
            pass
                   
    def get_cred(self, username):
        try:
            stmt = "SELECT FIRST_NAME,LAST_NAME,PASSWORD,STATUS,LOCKED,USER_TYPE  from ccndb.USERS where status='ACTIVE' and USERNAME = '" + username + "'"
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(stmt)
            ret_obj = {}
            for row in cursor:
                ret_obj["FIRST_NAME"] = row[0]
                ret_obj["LAST_NAME"] = row[1]
                ret_obj["PASSWORD"] = row[2]
                ret_obj["STATUS"] = row[3]
                ret_obj["LOCKED"] = row[4]
                ret_obj["USER_TYPE"] = row[5]
                break
            return ret_obj
        except Exception as e:
            return e
        
    
    