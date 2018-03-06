import sys
import pickle
import json

# +++your code here+++
# Define print_words(filename) and print_top(filename) functions.
def logparser(log_file):
  
  print '### LOGGING : Log Parser Running...\n'

  f = log_file

  # calculate list of words with respective count in file    
  
  columns = ["Site ID"]
  rows_of_phints = []
  rows_of_site_ids = []

  # Define phint_puller(data) function to pull out phints and values
  def phint_puller(data):

    phint_list = data.split('phint=')

    phints = {}

    for allphints in phint_list:

      if not allphints.startswith('/site/'):    
        
        if "%3D" in allphints:
          phint_name = allphints.split('%3D')[0].replace("%20"," ")        
          phint_value = allphints.split('%3D')[1].split('&')[0]
          phints[phint_name] = phint_value


        elif "=" in allphints:

          phint_name = allphints.split('=')[0].replace("%20","")  
          phint_value = allphints.split('=')[1].split('&')[0]
          phints[phint_name] = phint_value

          #print phint_name + "=" + phint_value

    
    return phints

  # Define column_adder(phints) to add new columns to list
  def column_adder(phints):

    for alldata in phints:

      if not alldata in columns:

        columns.append(alldata)

  # loop through all lines in file
  for line in f:   

    if line:

      line_split = line.split("\t") # split line by tabs
      site_id = line_split[1] # grab site ID
      data = line_split[2].replace('\n',"") # grab pixel string from line

      # return all phints in object
      phints = phint_puller(data)  


      # add phint to columns
      column_adder(phints) 

      # add phints
      rows_of_phints.append(phints)
      rows_of_site_ids.append(site_id)

  # loop through all rows and create a csv-formatted list per row
  rows = []

  for allphints in rows_of_phints:
    
    row_data = [""] * len(columns)    

    # push phint values in correct order into row
    for eachphint in allphints:
      
      # create row_data list with empty strings          
      insert_place = columns.index(eachphint)
      row_data[insert_place] = allphints[eachphint]      
          
    rows.append(row_data)
  
  # Push in siteIDs into rows
  for mylines in enumerate(rows):

    iteration_number = mylines[0]      
    mylines[1][0] = rows_of_site_ids[iteration_number]
    #print mylines, len(mylines[1])

  rows.insert(0,columns) # add columns at top of file

  print '### LOGGING : CSV Ready to be generated...\n'

  # write CSV
  import csv
  import datetime
  import time 
  import os
  import StringIO
  from flask import Response
  
  # set file name
  trimmed_file_name = log_file.filename.split('.')[0]
  currenttime = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d_%H-%M-%S')
  csvfilename = trimmed_file_name + "_" + currenttime + ".csv"

  # add useful info to top of CSV
  rows.insert(0,[" "])
  rows.insert(0,["Author : roshan.gonsalkorale@oracle.com"])
  rows.insert(0,[" "])
  rows.insert(0,["###############################"])
  rows.insert(0,["LOG WATCHER EXPORT FORMATTER"])
  rows.insert(0,["###############################"])
    
  def iter_csv(data):
    line = StringIO.StringIO()
    writer = csv.writer(line)
    for csv_line in data:
        writer.writerow(csv_line)
        line.seek(0)
        yield line.read()
        line.truncate(0)

  response = Response(iter_csv(rows), mimetype='text/csv')
  response.headers['Content-Disposition'] = 'attachment; filename=' + csvfilename

  print '### LOGGING : CSV Generated...\n'
  
  return response

def categoryCampaignQueue(publicKey,privateKey,categoryID,requestID):

  print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignQueue() started"
    
  import os
  import urllib
  import urllib2
  import cookielib
  import urlparse
  import hashlib 
  import hmac
  import base64
  import random

  # FUNCTION : apiHelper
  def apiCall(apiURL,requestType,data,publicKey,privateKey):

    #print "\nAPICALL : apiCall() started"
    Url = apiURL

    if(requestType == "GET"):
      newUrl = signatureInputBuilder(Url, 'GET', None,publicKey,privateKey)
      api_call = doRequest(newUrl, 'GET', None)
      return api_call

    elif(requestType == "POST"):
      newUrl = signatureInputBuilder(Url, 'POST', data,publicKey,privateKey)
      api_call = doRequest(newUrl, 'POST', data)
      return api_call

    elif(requestType == "PUT"):
      newUrl = signatureInputBuilder(Url, 'PUT', data,publicKey,privateKey)
      api_call = doRequest(newUrl, 'PUT', data)
      return api_call

    elif(requestType == "DELETE"):
      newUrl = signatureInputBuilder(Url, 'DELETE', None,publicKey,privateKey)
      api_call = doRequest(newUrl, 'DELETE', None)
      return api_call          

  # FUNCTION : Signature Builder
  def signatureInputBuilder(url, method, data,publicKey,bksecretkey):

      #print "\nSIGNATUREINPUTBUILDER : signatureInputBuilder() started\n"
      stringToSign = method
      parsedUrl = urlparse.urlparse(url)
      #print parsedUrl
      stringToSign += parsedUrl.path
      
      # splitting the query into array of parameters separated by the '&' character
      #print parsedUrl.query
      qP = parsedUrl.query.split('&')
      #print qP

      if len(qP) > 0:
          for  qS in qP:
              qP2 = qS.split('=')
              #print qP2
              if len(qP2) > 1:
                  stringToSign += qP2[1]
      
      #print stringToSign
      if data != None :
          stringToSign += data 
      #print "\nString to be Signed:\n" + stringToSign
      
      h = hmac.new(str(bksecretkey), str(stringToSign), hashlib.sha256)

      s = base64.standard_b64encode(h.digest())
      #print "\nRaw Method Signature:\n" + s 
      
      u = urllib.quote_plus(s)
      #print "\nURL Encoded Method Signature (bksig):\n" + u

      newUrl = url 
      if url.find('?') == -1 :
          newUrl += '?'
      else:
          newUrl += '&'
          
      newUrl += 'bkuid=' + publicKey + '&bksig=' + u 

      return newUrl

  # FUNCTION : apiCall
  def doRequest(url, method, data):

      #print "\nDOREQUEST : doRequest() started"
      headers = {"Accept":"application/json","Content-type":"application/json","User_Agent":"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5"}
      try:
          cJ = cookielib.CookieJar()
          request = None
          if method == 'PUT': 
              request = urllib2.Request(url, data, headers)
              request.get_method = lambda: 'PUT'
          elif  method == 'DELETE' :
              request = urllib2.Request(url, data, headers)
              request.get_method = lambda: 'DELETE'
          elif data != None :
              request = urllib2.Request(url, data, headers)
          else:
              request = urllib2.Request(url, None, headers)  
              opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cJ))
              
              u = opener.open(request)
              rawData = u.read()
              #print "\nResponse Code: 200"
              #print "\nAPI Response:\n" + rawData + "\n"
              #apiResponseParser(rawData,None)
              return rawData

      except urllib2.HTTPError, e:
          print "\nHTTP error: %d %s" % (e.code, str(e)) 
          print "ERROR: ", e.read()
          return None
      except urllib2.URLError, e:
          print "Network error: %s" % e.reason.args[1]
          print "ERROR: ", e.read()
          return None

  # 1 RETURN AUDIENCE LIST AND GET LIST OF IDS

  # 1a Call Audiences API to get list of audiences
  print "\nAUDIENCE GRAB : grabbing audiences"
  urlRequest = "http://services.bluekai.com/Services/WS/audiences"
  all_audiences = apiCall(urlRequest,"GET",None,publicKey,privateKey)
  print "AUDIENCE GRAB : audiences should be returned"

  # 1b Loop through returned audience list, grab Audience IDs and put in list
  print "\nAUDIENCE PARSE : getting list of all audience IDs"
  audience_ids = []
  all_audiences = json.loads(all_audiences)

  for audiences in all_audiences["audiences"]:
    audience_ids.append(audiences["id"])

  print "AUDIENCE PARSE : List of IDs returned (see below)\n"
  print audience_ids

  # 2 LOOP THROUGH EACH AUDIENCE, CHECK IF CATEGORY ID PRESENT, NOTE AUDIENCE THEN LOOK UP CAMPAIGN  
  print "\nAUDIENCE CATEGORY SEARCH : Checking each audience for category ID '" + categoryID + "'\n"
  audiences = {}
  
  # 2a Check each audience
  audience_call_number = 1

  for audience_id in audience_ids:
  
    print "AUDIENCE CATEGORY SEARCH : Audience call " + str(audience_call_number) + " : Audience ID = " + str(audience_id)
    audience_call_number = audience_call_number +1
    audience_id = str(audience_id)
    urlRequest = "http://services.bluekai.com/Services/WS/audiences/"+audience_id
    returned_audience = apiCall(urlRequest,"GET",None,publicKey,privateKey)      

    # 2b Check each for Category ID
    
    result = returned_audience.find('cat" : '+ str(categoryID) + ',')
    print "AUDIENCE CATEGORY SEARCH : Checking audience '" + audience_id + " for category ID '" + categoryID + "'"
    if result == -1:
        found = False
        print "AUDIENCE CATEGORY SEARCH : Category not found"
    else:
        found = True
        print "AUDIENCE CATEGORY SEARCH : Category FOUND"
    
    # 2c If found, note the audience ID + name and note campaign names
    if found:

        returned_audience = json.loads(returned_audience)

        audiences[audience_id] = {}        
        audiences[audience_id]["audience_name"] = returned_audience["name"]
        audiences[audience_id]["audience_id"] = returned_audience["id"]
        audiences[audience_id]["campaigns"] = []

        print "AUDIENCE CATEGORY SEARCH : Audience ID='" + str(returned_audience["id"]) + "' | Audience Name='" + returned_audience["name"] + "'"        

        for campaign in returned_audience["campaigns"]:

            audiences[audience_id]["campaigns"].append(campaign)            

            print "AUDIENCE CATEGORY SEARCH : Campaign ID='" + str(campaign["id"]) + "' | Campaign Name='" + campaign["name"] + "'"        

  print "\nALL AUDIENCES CAMPAIGNS CHECKED : Results below"

  # Writing results to data
  this_request = {}
  this_request["data"] = audiences
  this_request["status"] = "completed"
  writeToMem(requestID,this_request)

def writeToMem(requestID,data):

  print "\nGLOBAL : writeToMem() called"
  global all_requests

  # if 'all_requests' does not exist in globals() : add it
  if "all_requests" not in globals():

    all_requests = {}

    print "'all_requests' not found in globals() : created (see below)"
    print all_requests

  # Adding request into 'all_requests'
  print "\nUpdating 'all_requests' with request " + requestID +  " = " + str(data) + " see below:"
  print data  

  all_requests[requestID] = data

def readFromMem(requestID):

  print "GLOBAL : readFromMem() called"
  global all_requests

  # if 'all_requests' not found in globals() then return
  if "all_requests" not in globals():

    print "No requests found"
    return "No requests found"
    
  else:

    # if 'all_requests' exists in globals() : add request
    if requestID in all_requests:
      print  "'all_requests' : found request = " + requestID + " : printing below and returning"
      print all_requests[requestID]
      return all_requests[requestID]

    else:

      print "\nRequest not found in 'all_requests' : returning"
      return "No requests found"
    
    
def clearFromMem(requestID):

  print "\nGLOBAL : clearFromMem() called"
  global all_requests

  if "all_requests" not in globals():

    print "No requests found"
    return "No requests found"
    
  else:
  
    print "\nGLOBAL : Deleting requestID=" + requestID + " from 'all_requests' object"
    del all_requests[requestID]            

def clearAllMem():

  print "\nGLOBAL : clearAllMem() called"
  global all_requests

  if "all_requests" not in globals():

    print "No requests found"
    return "No requests found"
      
  else:

    all_requests = {}

    print "\nClearing 'all_requests'"    
    
def categoryCampaignCheck(requestID):

  print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck() started"
  print "requestID = " + requestID
  print ""  

  #Check Pickle for request
  request_data = readFromMem(requestID)
  
  # If no data yet : return 'not completed'
  if request_data == "No requests found":

    print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck(",requestID,") : no data found in Pickle : returning {'status':'not competed'}"
    data = {"status":"not completed - no requests found yet"}
    #print "DUMPING DATA 2 !!!"
    return json.dumps(data)

  # If data : return data (and remove from 'all_requests' if 'completed')
  else:
    
    print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck(",requestID,") : data found in 'all_requests' : see returned below:"
    print request_data
    print ""

    # Remove from mem if request completed    
    if request_data["status"] == "completed":
      
      print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck(",requestID,") : removing request from 'all_requests' as no longer required"

      clearFromMem(requestID)
      return json.dumps(request_data)

    if request_data["status"] == "not completed":

      print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck(",requestID,") : status is 'not completed'"
                  
      return json.dumps(request_data)
    
    else:
      
      # return requst data back
      return request_data


