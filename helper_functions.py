import sys

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

def categoryCampaignCheck(publicKey,privateKey,categoryID):

  # FUNCTION : apiHelper
  def apiCall(apiURL,requestType,data,publicKey,privateKey):

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
      
      h = hmac.new(bksecretkey, stringToSign, hashlib.sha256)

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

