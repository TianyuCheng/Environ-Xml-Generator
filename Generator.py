#!/usr/bin/env python

from GoogleReader import SpreadsheetReader
from Generate_XML import *

callbacks = [generate_regions, generate_bases, \
             generate_events, generate_upgrades, generate_costs, \
             generate_effects, generate_probabilities, generate_range_conditions, \
             generate_prereq_conditions]

def generate_all(reader):
    for index in xrange(len(worksheets) - 1):
        callbacks[index](reader)

if __name__ == '__main__':

    # select from the menu first
    worksheet_id = menu()

    # set up username
    username = "skysource.tony@gmail.com"

    # set up GoogleSpreadSheetReader
    reader = SpreadsheetReader(username, "BaseNodeInfo")

    if worksheet_id == 0:
        generate_all(reader)
    else:
        callbacks[worksheet_id - 1](reader)
