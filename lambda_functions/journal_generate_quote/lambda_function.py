import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier
import urllib.parse
import string
import requests
from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: journal_generate_quote**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'benfordapp-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    
    configur = ConfigParser()
    configur.read(config_file)
    
    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')
    
    #
    # get uid from api gateway url parameters:
    #
    uid = event['queryStringParameters']['uid']
    print("uid:", uid)

    #
    # open connection to the database:
    # then grab the most recent 
    # sleep, eat, water, social, overall, and notes from the database
    print("**Opening DB connection**")
    #
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    #
    sql = """
      SELECT notes, sleep, eat, water, social, overall
      FROM entries where uid = %s
    """
    #
    data = datatier.retrieve_all_rows(dbConn, sql, uid)
    
    print(data)

    #
    # done!
    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning success**")
    
    return {
      'statusCode': 200,
      'body': json.dumps("success")
    }
    
  #
  # on an error, try to upload error message to S3:
  #
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    #
    # done, return:
    #    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }