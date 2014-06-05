#!/usr/bin/env python

import os

worksheets = ["all", "regions", "bases", "events", \
              "upgrades", "costs", "effects", "probability", \
              "range_conditions", "prereq_conditions"]

def menu():
    """@todo: menu for options
    :returns: @id of worksheet
    """
    for index, worksheet in enumerate(worksheets):
        print "%d) %s" % (index, worksheet)

    print "-----------------------------------------------------"
    print "Input the worksheet id that you want to work on"
    option = input("Input: ")

    if not os.path.exists("./xmls"):
        print "xmls directory not found; try generating it"
        os.makedirs("./xmls")

    print "you are trying to generate", worksheets[option], "xml"
    print "-----------------------------------------------------"
    return option

def generate_regions(reader):
    entries = reader.read_worksheet(1)

def generate_bases(reader):
    entries = reader.read_worksheet(1)

def generate_events(reader):
    entries = reader.read_worksheet(1)

def generate_upgrades(reader):
    entries = reader.read_worksheet(1)

def generate_costs(reader):
    entries = reader.read_worksheet(1)

def generate_effects(reader):
    entries = reader.read_worksheet(1)

def generate_probabilities(reader):
    entries = reader.read_worksheet(1)

def generate_range_conditions(reader):
    entries = reader.read_worksheet(1)

def generate_prereq_conditions(reader):
    entries = reader.read_worksheet(1)
