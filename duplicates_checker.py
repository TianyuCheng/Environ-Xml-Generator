#!/usr/bin/env python

# append current path to syspath
import os, sys
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from Generate_XML import *
from Check_XML import *

callbacks = [check_regions, check_bases, \
             check_events, check_upgrades, check_costs, \
             check_effects, check_probabilities, check_range_conditions, \
             check_prereq_conditions]

def check_all(reader):
    for index in xrange(len(worksheets) - 1):
        callbacks[index](reader)

if __name__ == '__main__':
    
    # select from the menu first
    worksheet_id = menu()

    # set up username or use the default account
    if len(sys.argv) >= 2:
        username = sys.argv[1]
    else:
        username = "skysource.tony@gmail.com"

    # set up GoogleSpreadSheetReader
    reader = SpreadsheetReader(username, "BaseNodeInfo")

    if worksheet_id == 0:
        check_all(reader)
    else:
        callbacks[worksheet_id - 1](reader)
