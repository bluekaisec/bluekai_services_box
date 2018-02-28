import os
import sys
import urllib
import urllib2
import cookielib
import urlparse
import hashlib 
import hmac
import base64
import json
import random

headers = {"Accept":"application/json","Content-type":"application/json","User_Agent":"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1) Gecko/20090624 Firefox/3.5"}

def categoryCampaignCheck(publicKey,privateKey,categoryID):

  print "\nCATEGORYCAMPAIGNCHECK : categoryCampaignCheck() started"

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
  
    print "AUDIENCE CATEGORY SEARCH : Audience call " + str(audience_call_number)
    audience_call_number = audience_call_number +1
    audience_id = str(audience_id)
    urlRequest = "http://services.bluekai.com/Services/WS/audiences/"+audience_id
    returned_audience = apiCall(urlRequest,"GET",None,publicKey,privateKey)      

    # 2b Check each for Category ID
    result = returned_audience.find('cat" : '+ categoryID + ',')
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


    print ""

  print "\nALL AUDIENCES CAMPAIGNS CHECKED : Results below"
  print audiences


# 2.  Specify the service endpoint
#    - For GET (List) requests, add the desired sort and filter options in the query string
#    - For GET (Read), PUT or DELETE requests, append the item ID to the Url path
#     * NOTE: For the Campaign, Order, and Pixel URL APIs, insert the item ID in the query string instead of the Url path

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

  print "API Call: \n" + newUrl
    

# 3. For POST and PUT requests, uncomment the "data" variable and enter the JSON body
#data = ''

#Creating the method signature
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

#Generating  the method request 
def doRequest(url, method, data):

    #print "\nDOREQUEST : doRequest() started"

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

def apiResponseParser(returnData,type):

    print "apiResponseParser() has run"

def main(argv=None):
    
    # Pass in your (api public key, api private key, category ID)
    categoryCampaignCheck("PUBLICKEY","PRIVATEKEY","CATEGORYID")
    
if __name__ == "__main__":
   main()