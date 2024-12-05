#
# Inserts a new entry record
# in the JournalApp database
#

import json
import os
import datatier
import time

from configparser import ConfigParser

def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: journal-app-upload**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'journalapp-config.ini'
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
    # the user has sent us two parameters:
    #  1. filename of their file
    #  2. raw file data in base64 encoded string
    #
    # The parameters are coming through web server 
    # (or API Gateway) in the body of the request
    # in JSON format.
    #
    print("**Accessing request body**")
    
    if "uid" not in event["pathParameters"]:
        raise Exception("event has no uid")
        
    uid = event["pathParameters"]["uid"]
    print("uid:", uid)

    if "body" not in event["queryStringParameters"]:
      raise Exception("event has no body")
      
    body = json.loads(event["queryStringParameters"]["body"]) # parse the json
    
    if "notes" not in body:
      raise Exception("event has a body but no notes")
    if "sleep" not in body:
      raise Exception("event has a body but no sleep")
    if "eat" not in body:
      raise Exception("event has a body but no eat")
    if "water" not in body:
      raise Exception("event has a body but no water")
    if "social" not in body:
      raise Exception("event has a body but no social")
    if "overall" not in body:
        raise Exception("event has a body but no overall")

    notes = body["notes"]
    sleep = body["sleep"]
    eat = body["eat"]
    water = body["water"]
    social = body["social"]
    overall = body["overall"]
    # get datetime sql format
    date = time.strftime('%Y-%m-%d %H:%M:%S')

    print("Got data from the client:")
    print("notes:", notes)
    print("sleep:", sleep)
    print("eat:", eat)
    print("water:", water)
    print("social:", social)
    print("overall:", overall)
    
    #
    # open connection to the database:
    #
    print("**Opening connection**")
    
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

    #
    # first we need to make sure the uid is valid:
    #
    print("**Checking if uid is valid**")
    
    sql = "SELECT * FROM users WHERE uid = %s;"
    
    row = datatier.retrieve_one_row(dbConn, sql, [uid])
    
    if row == ():  # no such user
      print("**No such user, returning...**")
      return {
        'statusCode': 400,
        'body': json.dumps("no such user...")
      }
    
    print(row)
    print("**Adding entries row to database**")
    
    sql = """
      INSERT INTO entries(uid, date, notes, sleep, eat, water, social, overall)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    #
    # Insert the entry into the database:
    #
    datatier.perform_action(dbConn, sql, [uid, date, notes, sleep, eat, water, social, overall])

    #
    # respond in an HTTP-like way, i.e. with a status
    # code and body in JSON format:
    #
    print("**DONE, returning ok**")
    
    return {
      'statusCode': 200,
      'body': "success"
    }
    
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }
