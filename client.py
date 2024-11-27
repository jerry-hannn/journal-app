#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law.
#
# Authors:
#   Jenny Zhou
#   Jerry Han
#   Joey Shao
#    
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import datatier
import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser

###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => users")
    """
    print("   2 => jobs")
    print("   3 => reset database")
    print("   4 => upload pdf")
    print("   5 => download results")
    print("   6 => upload and poll")"""

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


def journal_upload(baseurl):
  try:
    sleep_score = input("Rate your sleep today on a scale from 0 to 10: ")
    food_score = input("Rate your nutrition today on a scale from 0 to 10: ")
    water_score = input("Rate your hydration today on a scale from 0 to 10: ")
    social_score = input("Rate your social connection today on a scale from 0 to 10: ")
    overall_score = input("Rate your overall day on a scale from 0 to 10: ")
    notes = input("If you'd like, journal about what happened today: ")

    body = {"sleep": sleep_score, "eat": food_score, "water": water_score, 
              "social": social_score, "overall_score": overall_score, "notes": notes}

    url = baseurl + "/upload-entry"
    res = requests.post(url, json=body)

  except:
    logging.error("**ERROR: journal_upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return



############################################################
# main
#
try:
  print('** Welcome to BenfordApp **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = "" # FIX THIS PART

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  print("Connecting to RDS...")
  endpoint = configur.get('rds', 'endpoint')
  portnum = (configur.get('rds', 'port_number'))
  username = configur.get('rds', 'user_name')
  pwd = configur.get('rds', 'user_pwd')
  dbname = configur.get('rds', 'db_name')

  dbConn = datatier.get_dbConn(endpoint, portnum, username, pwd, dbname)
  dbCursor = dbConn.cursor()

  if dbConn is None:
    print('**ERROR: unable to connect to database, exiting')
    sys.exit(0)
  
  user_id = input("Please enter your user ID: ")
  sqlUser = """
      SELECT * from users WHERE userid = %s;
      """
  
  dbCursor.execute(sqlUser, [user_id])
  user = dbCursor.fetchone()
  
  if user is None or user == ():
      print("No such user...")
  else:
    baseurl += "/" + str(user_id)
    print("User successfully found!")

  cmd = prompt()
  while cmd != 0:
    #
    if cmd == 1:
      journal_upload(baseurl)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
