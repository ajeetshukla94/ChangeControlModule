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
from flask import session
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
            stmt = "SELECT FIRST_NAME,LAST_NAME,PASSWORD,STATUS,LOCKED,USER_DEPARTMENT,USER_LEVEL  from ccndb.USERS where status='ACTIVE' and USERNAME = '" + username + "'"
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
                ret_obj["USER_DEPARTMENT"] = row[5]
                ret_obj["USER_LEVEL"] = row[6]
                break
            return ret_obj
        except Exception as e:
            return e
        
    def fetch_application_statuses(self):
        try:
            stmt = "SELECT DISTINCT Application_Status FROM ccndb.change_control_master"
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(stmt)
            statuses = [row[0] for row in cursor]
            return statuses
        except Exception as e:
            return []
        
    def insert_change_control_data(self, area_of_change, initiator_department, description, existing_status, proposed_change, reason_justification, **kwargs):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()

            insert_master_query = """
            INSERT INTO ccndb.change_control_master
            (Area_of_Change, Affects_Initiator_Department, Change_Description, Existing_Status, Proposed_Change, Change_Reason)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(insert_master_query, (area_of_change, initiator_department, description, existing_status, proposed_change, reason_justification))
            conn.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            last_inserted_id = cursor.fetchone()[0]

            print(f"Last Inserted ID: {last_inserted_id}")

            statuses = self.fetch_application_statuses()

            for department in ['Production', 'QC', 'QA', 'Store', 'Engineering', 'HR', 'Admin']:
                if kwargs.get('level') == 'hod':
                    for status in statuses:
                        insert_audit_query = """
                        INSERT INTO ccndb.change_control_audit
                        (Application_id, Status, Timestamp, Username, Department, Level, Remark)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        username = session['session_var']['USER_NAME']

                        try:
                            cursor.execute(insert_audit_query, (last_inserted_id, status, timestamp, username, department, kwargs.get('level'), ''))
                            conn.commit()

                            print(f"Audit Record Inserted for Department: {department}, Status: {status}")
                        except Exception as e:
                            print(f"Error inserting audit data: {str(e)}")


            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error inserting data into the database: {str(e)}")

    def fetch_audit_data_for_department(self, department):
        try:
            stmt = """
            SELECT a.Audit_id, m.Application_id, a.Status
            FROM ccndb.change_control_audit a
            JOIN ccndb.change_control_master m ON a.Application_id = m.Application_id
            WHERE a.Department = %s
            ORDER BY a.Timestamp DESC
            """
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(stmt, (department,))

            audit_data = cursor.fetchall()

            return audit_data
        except Exception as e:
            print(f"Error fetching audit data: {str(e)}")
            return []
        
    def get_audit_data_by_id(self, audit_id):
        try:
            stmt = """
            SELECT m.Application_id, m.Area_of_Change, m.Affects_Initiator_Department, m.Change_Description,
                   m.Existing_Status, m.Proposed_Change, m.Change_Reason,
                   a.Status as Audit_Status, a.Timestamp as Audit_Timestamp, a.Username, a.Remark
            FROM ccndb.change_control_master m
            JOIN ccndb.change_control_audit a ON m.Application_id = a.Application_id
            WHERE a.Audit_id = %s
            """
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor(dictionary=True)

            cursor.execute(stmt, (audit_id,))

            audit_data = cursor.fetchone()

            print(f"Audit Data for Audit ID {audit_id}: {audit_data}")

            return audit_data
        except Exception as e:
            print(f"Error fetching audit data by ID: {str(e)}")
            return None
        

    def update_audit_data(self, audit_id, approval, remark):
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()

            update_query = """
            UPDATE ccndb.change_control_audit
            SET Status = %s, Remark = %s
            WHERE Audit_id = %s
            """

            cursor.execute(update_query, (approval, remark, audit_id))
            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error updating audit data: {str(e)}")