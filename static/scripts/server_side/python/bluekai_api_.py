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

# 1. Enter your BlueKai developer keys

bkuid = 'e90228f78e4802a797818fe19af732d2a120132687eaa6694b92ffa682160bf5' #Web Service User Key
bksecretkey = '349dc7c6ef8c8ab9127602aa17fe2679a1049c62856c28d4e57457a19b190f77' #Web Service Private Key

# 2.  Specify the service endpoint
#    - For GET (List) requests, add the desired sort and filter options in the query string
#    - For GET (Read), PUT or DELETE requests, append the item ID to the Url path
#     * NOTE: For the Campaign, Order, and Pixel URL APIs, insert the item ID in the query string instead of the Url path

Url = 'http://services.bluekai.com/Services/WS/Ping'

# 3. For POST and PUT requests, uncomment the "data" variable and enter the JSON body
#data = ''

#Creating the method signature
def signatureInputBuilder(url, method, data):
    stringToSign = method
    parsedUrl = urlparse.urlparse(url)
    print parsedUrl
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
    print "\nString to be Signed:\n" + stringToSign
    
    h = hmac.new(bksecretkey, stringToSign, hashlib.sha256)

    s = base64.standard_b64encode(h.digest())
    print "\nRaw Method Signature:\n" + s 
    
    u = urllib.quote_plus(s)
    print "\nURL Encoded Method Signature (bksig):\n" + u

    newUrl = url 
    if url.find('?') == -1 :
        newUrl += '?'
    else:
        newUrl += '&'
        
    newUrl += 'bkuid=' + bkuid + '&bksig=' + u 

    return newUrl

#Generating  the method request 
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
            print "\nResponse Code: 200"
            print "\nAPI Response:\n" + rawData + "\n"
            return rawData

    except urllib2.HTTPError, e:
        print "\nHTTP error: %d %s" % (e.code, str(e)) 
        print "ERROR: ", e.read()
        return None
    except urllib2.URLError, e:
        print "Network error: %s" % e.reason.args[1]
        print "ERROR: ", e.read()
        return None

#4. Specify the API request method 
def main(argv=None):
    
    # Select the API Method by uncommenting the newUrl reference variable and doRequest() method
    
    # GET
    newUrl = signatureInputBuilder(Url, 'GET', None)
    doRequest(newUrl, 'GET', None)
    
    # POST
    #newUrl = signatureInputBuilder(Url, 'POST', data)
    #doRequest(newUrl, 'POST', data)
    
    # PUT
    #newUrl = signatureInputBuilder(Url, 'PUT', data)
    #doRequest(newUrl, 'PUT', data)
    
    #DELETE
    #newUrl = signatureInputBuilder(Url, 'DELETE', None)
    #doRequest(newUrl, 'DELETE', None)
    
    print "API Call: \n" + newUrl

if __name__ == "__main__":
   main()