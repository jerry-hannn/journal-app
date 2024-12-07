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

import pymysql
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
    print("   1 => journal_upload")
    print("   2 => picture_upload")
    print("   3 => get_quote")
    print("   4 => journal_download")
    print("   5 => get_stats")

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

def valid_status_code(res, url):
    if res.status_code == 200: #success
      return True
    elif res.status_code == 400: # no such user
      body = res.json()
      print(body)
      return False
    else:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        body = res.json()
        print("Error message from server:", body)
      return False



def journal_upload(baseurl):
  url = baseurl + "/upload-entry/" + userid
  try:
    print("For all ratings, please type in an integer!")
    sleep_score = int(input("Rate your sleep today on a scale from 0 to 10: "))
    food_score = int(input("Rate your nutrition today on a scale from 0 to 10: "))
    water_score = int(input("Rate your hydration today on a scale from 0 to 10: "))
    social_score = int(input("Rate your social connection today on a scale from 0 to 10: "))
    overall_score = int(input("Rate your overall day on a scale from 0 to 10: "))

    scores = [sleep_score, food_score, water_score, social_score, overall_score]
    for score in scores:
      if score > 10 or score < 0:
        print("Please make sure your scores are between 0 and 10!")
        return

    notes = input("If you'd like, journal about what happened today: ")

    body = {"sleep": sleep_score, "eat": food_score, "water": water_score, 
              "social": social_score, "overall": overall_score, "notes": notes}

    res = requests.post(url, json=body)

    if valid_status_code(res, url):
      print("Successfully uploaded entry!")
    else:
      return

  except Exception as e:
    logging.error("**ERROR: journal_upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def picture_upload(baseurl):
  url = baseurl + "/upload-image/" + userid
  try:
    print("Enter picture filename>")
    local_filename = input()

    if not pathlib.Path(local_filename).is_file():
      print("Image '", local_filename, "' does not exist...")
      return

    infile = open(local_filename, "rb")
    bytes = infile.read()
    infile.close()

    datastr = ""
    
    data = base64.b64encode(bytes)
    datastr = data.decode('utf-8')

    data = {"filename": local_filename, "data": datastr}

    res = requests.post(url, json=data)

    if valid_status_code(res, url):
      pass
    else:
      return

    print("Image uploaded successfully!")
    return

  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def get_quote(baseurl):
  url = baseurl + "/generate-quote/" + userid
  try:
    print("Waiting for quote generation...")
    res = requests.get(url)

    if valid_status_code(res, url):
      print(res.json()['quote'])
    else:
      return
  
  except Exception as e:
    logging.error("**ERROR: upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

def journal_download(baseurl):
  url = baseurl + "/download-collage/" + userid
  try:
    print("Waiting for collage to download...")
    res = requests.get(url)

    if valid_status_code(res, url):
      filename = input("Please type what you would like to name the collage - a .jpg extension will be added to whatever you write: ")
      filename += ".jpg"
      with open(filename, "wb") as file:
                body = res.json()
                bytes = base64.b64decode(body["collage"])
                file.write(bytes)
                print("Collage downloaded successfully as", filename)
    else:
      return
  except Exception as e:
    logging.error("**ERROR: journal_upload() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def get_stats(baseurl):
  url = baseurl + "/stats/" + userid
  try:
    print("Waiting for collection of stats...")
    res = requests.get(url)

    if valid_status_code(res, url):
        print("Here is a ranking of which factors impact your overall day most: ")
        factors_list = ["sleep", "eat", "water", "social"]
        coefficients = res.json()["coef"]
        
        factors_ranked = sorted(zip(factors_list, coefficients), key=lambda x: abs(x[1]), reverse=True)
        for i, factor in enumerate(factors_ranked):  
            print(f"    {i+1}. {factor[0]}: {'negatively' if factor[1] < 0 else 'positively'} impacts your day with score {round(factor[1],2)}")

    else:
      return
    
  except Exception as e:
    logging.error("**ERROR: get_stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
def get_entries(baseurl):
  url = baseurl + "/get-entries/" + userid
  try:
    print("Waiting for server to return entries...")
    res = requests.get(url)

    if valid_status_code(res, url):
        #TODO
        print("TODO")

    else:
      return
    
  except Exception as e:
    logging.error("**ERROR: get_stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def get_specific_entry(baseurl):
  url = baseurl + "/get-entries/" + userid
  entryID = input("Input the ID of the entry you'd like to read: ")
  try:
    print("Waiting for server to return entries...")
    res = requests.get(url)

    if valid_status_code(res, url):
        #TODO
        print("TODO")

    else:
      return
    
  except Exception as e:
    logging.error("**ERROR: get_stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return



def get_dbConn(endpoint, portnum, username, pwd, dbname):
  try:
    dbConn = pymysql.connect(host=endpoint,
                             port=int(portnum),
                             user=username,
                             passwd=pwd,
                             database=dbname)

                        
                          
    return dbConn
  
  except Exception as e:
    logging.error("datatier.get_dbConn() failed:")
    logging.error(e)
    return None

############################################################
# main
#
try:
  print('** Welcome to JournalApp **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = "journalapp-config.ini"

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
  portnum = configur.get('rds', 'port_number')
  username = configur.get('rds', 'user_name')
  pwd = configur.get('rds', 'user_pwd')
  dbname = configur.get('rds', 'db_name')

  dbConn = get_dbConn(endpoint, portnum, username, pwd, dbname)
  dbCursor = dbConn.cursor()

  if dbConn is None:
    print('**ERROR: unable to connect to database, exiting')
    sys.exit(0)

  
  while True:
    username = input("Please enter your username: ")
    sqlUser = """
        SELECT * from users WHERE username = %s;
        """
    
    dbCursor.execute(sqlUser, [username])
    userRow = dbCursor.fetchone()
    
    if userRow is None or userRow == ():
        print("No such user...")
        continue
    else:
      userid = str(userRow[0])
      print("User successfully found with userid", userid)
      break

  cmd = prompt()
  while cmd != 0:
    #
    if cmd == 1:
      journal_upload(baseurl)
    elif cmd == 2:
      picture_upload(baseurl)
    elif cmd == 3:
      get_quote(baseurl)
    elif cmd == 4:
      journal_download(baseurl)
    elif cmd == 5:
      get_stats(baseurl)
    elif cmd == 6:
      get_entries(baseurl)
    elif cmd == 7:
      get_specific_entry(baseurl)
      
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()


  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)


    
