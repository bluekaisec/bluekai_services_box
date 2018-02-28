# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import io

app = Flask(__name__)

print '\n### LOGGING : Flask started ###\n'

@app.route('/')

def index():
    
    return render_template('index.html')

# CSV CONVERTER : START
@app.route('/log_watcher_url_parser')

def log_watcher_url_parser():
    return render_template('log_watcher_url_parser.html')

@app.route('/log_watch_upload', methods=["POST"])

def log_watch_upload():
    
    uploaded_file = request.files.get('log_watch_file') # Grab submitted file
    
    print '### LOGGING : " ',uploaded_file,' "file received ###\n'
      
    # import log watch parser
    from helper_functions import logparser

    converted_csv = logparser(uploaded_file)

    print '### LOGGING : Printing CSV ###\n'

    print '### LOGGING : ',str(converted_csv)

    try:
        
        str(converted_csv) == "<Response streamed [200 OK]>"        
    
    except ExceptionI:

        converted_csv = "fail"        
        
    print converted_csv
    return converted_csv

    #return render_template('csv.html')
    
# CSV CONVERTER : END

# GOOGLE TAG MANAGER TEST PAGE : START
@app.route('/google_tag_manager_test_page')

def google_tag_manager_test_page():
    return render_template('google_tag_manager_demo_page.html')
# GOOGLE TAG MANAGER TEST PAGE : END

# CATEGORY AUDIENCE/CAMAPAIGN GRABBER : START
@app.route('/category_campaign_grabber')

def category_campaign_grabber():
    return render_template('category_campaign_grabber.html')

@app.route('/category_campaign_grabber_details', methods=["POST"])

def category_campaign_grabber_submit():
    
    #WRITE CODE TO GRAB FIELDS
    #uploaded_file = request.files.get('log_watch_file') # Grab submitted file

    apiPublicKey = request.form['apiPublicKey']
    apiSecretKey = request.form['apiSecretKey']
    categoryID = request.form['categoryID']
              
    # import log watch parser
    from helper_functions import categoryCampaignCheck

    #publicKey = "e90228f78e4802a797818fe19af732d2a120132687eaa6694b92ffa682160bf5" # CHANGE
    #privateKey = "349dc7c6ef8c8ab9127602aa17fe2679a1049c62856c28d4e57457a19b190f77" # CHANGE
    #categoryID = "611839" # CHANGE

    campaigns = categoryCampaignCheck(publicKey,privateKey,categoryID)
    
    return campaigns

    print campaigns

# CATEGORY AUDIENCE/CAMAPAIGN GRABBER : END


@app.errorhandler(500)

def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500