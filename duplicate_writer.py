#!/usr/bin/env python

# append current path to syspath
import os, sys
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from Generate_XML import *
from Check_XML import *

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
    reader = SpreadsheetReader(username, "XmlGameData.gsheet")
    feeds = reader.get_worsksheet_feeds(lambda s : s.split(' ')[0])
    option = reader.menu()
