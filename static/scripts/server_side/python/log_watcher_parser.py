#!/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Google's Python Class
# http://code.google.com/edu/languages/google-python-class/

"""Wordcount exercise
Google's Python class

The main() below is already defined and complete. It calls print_words()
and print_top() functions which you write.

1. For the --count flag, implement a print_words(filename) function that counts
how often each word appears in the text and prints:
word1 count1
word2 count2
...

Print the above list in order sorted by word (python will sort punctuation to
come before letters -- that's fine). Store all the words as lowercase,
so 'The' and 'the' count as the same word.

2. For the --topcount flag, implement a print_top(filename) which is similar
to print_words() but which prints just the top 20 most common words sorted
so the most common word is first, then the next most common, and so on.

Use str.split() (no arguments) to split on all whitespace.

Workflow: don't build the whole program at once. Get it to an intermediate
milestone and print your data structure and sys.exit(0).
When that's working, try for the next milestone.

Optional: define a helper function to avoid code duplication inside
print_words() and print_top().

"""

import sys

# +++your code here+++
# Define print_words(filename) and print_top(filename) functions.
def logparser(log_file):
  
  f = log_file

  # calculate list of words with respective count in file  

  print '\nSTARTING LOG WATCHER CSV CONVERTED :  will convert log watcher txt into CSV and drop into folder of your python script\n'
  
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
          phint_name = allphints.split('%3D')[0]        
          phint_value = allphints.split('%3D')[1].split('&')[0]
          phints[phint_name] = phint_value


        elif "=" in allphints:

          phint_name = allphints.split('=')[0]        
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

  #for all_lines in rows:
    #print all_lines

  """
  # write CSV
  import csv
  import datetime
  import time 
  import os
  
  
  # define get_script_dir() to get location of python script
  import inspect

  def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

  # set file name
  currenttime = datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d_%H_%M_%S')
  csvfilename = "log_watcher_csv_formatter_" + currenttime


  # grab script directory
  localfolder = get_script_dir()

  # set where to drop script
  csv_location_and_name = localfolder + "/" + csvfilename+".csv"

  with open(csv_location_and_name, 'wb') as csvfile:
    
    row_writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)

    row_writer.writerow(["###############################"])
    row_writer.writerow(["LOG WATCHER EXPORT FORMATTER"])
    row_writer.writerow(["###############################"])
    row_writer.writerow([" "])
    row_writer.writerow(["Author : roshan.gonsalkorale@oracle.com"])
    row_writer.writerow([" "])
    
    for all_lines in rows:

      row_writer.writerow(all_lines)

    print "COMPLETED\n"

    print "File generated : " + csvfilename + ".csv"
    print "Dropped into: " + localfolder + "\n"
  """
  f.close()

# You could write a helper utility function that reads a file
# and builds and returns a word/count dict for it.
# Then print_words() and print_top() can just call the utility function.

###

# This basic command line argument parsing code is provided and
# calls the print_words() and print_top() functions which you must define.
def main():
    
if __name__ == '__main__':
  main()