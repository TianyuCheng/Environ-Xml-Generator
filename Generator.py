#!/usr/bin/env python

# append current path to syspath
import os, sys
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from Check_XML import *
from Generate_XML import *

def generate_all(reader, options):
    for key, value in options.iteritems():
        eval("generate_" + key.lower() + "(reader, \"" + value + "\")")

def check_all(reader, options):
    for key, value in options.iteritems():
        eval("check_" + key.lower() + "(reader, \"" + value + "\")")

if __name__ == '__main__':

    # set up username or use the default account
    if len(sys.argv) >= 2:
        username = sys.argv[1]
    else:
        username = "skysource.tony@gmail.com"

    # set up GoogleSpreadSheetReader
    # reader = SpreadsheetReader(username, "BaseNodeInfo.gsheet")
    reader = SpreadsheetReader(username, "BaseNodeInfo2.gsheet")
    feeds = reader.get_worsksheet_feeds(lambda s : s.split(' ')[0])
    option = reader.menu()

    # mkdir if directory not found
    if not os.path.exists("./xmls"):
        print "xmls directory not found; try generating iit"
        os.makedirs("./xmls")

    print "-----------------------------------------------------"


    if isinstance(option, dict):       # generate all xmls
        check_all(reader, option)
        generate_all(reader, option)
    else:                               # generate single xml
        eval("generate_" + option[0].lower() + "(reader, option[1])")
        eval("check_" + option[0].lower() + "(reader, option[1])")
