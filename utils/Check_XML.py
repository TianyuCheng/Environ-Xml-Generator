# import regular expression
import os, re

def stringify(entry, *args):
    ret = [entry.custom[arg].text for arg in args]
    return str(ret)

def check_duplicates(entries, primary_key, *args):
    # create a new dictionary to check duplicates
    entries_dict = dict()
    
    # check each entry
    for entry in entries:
        current_id = entry.custom[primary_key].text
        if current_id is not None:
            key = stringify(entry, *args)
            # print "==========", key, "==========="
            if key in entries_dict:
                print "entry id %s repeats entry id %s : %s" % (current_id, entries_dict[key], key)
            else:
                entries_dict[key] = current_id


def check_regions(reader):
    print "No need to check duplicates in regions"

def check_bases(reader):
    print "No need to check duplicates in bases"

def check_events(reader):
    print "No need to check duplicates in events"

def check_upgrades(reader):
    print "No need to check duplicates in upgrades"

def check_costs(reader):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(5)
    check_duplicates(entries, 'id', 'duration', 'amount', 'rangeconditions')

def check_effects(reader):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(6)
    check_duplicates(entries, 'id', 'score', 'duration', 'area', 'amount')

def check_probabilities(reader):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(7)
    check_duplicates(entries, 'id', 'rangeconditions', 'prereqconditions')

def check_range_conditions(reader):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(8)
    check_duplicates(entries, 'id', 'score', 'low', 'high', 'multiplier')

def check_prereq_conditions(reader):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(9)
    check_duplicates(entries, 'id', 'keys', 'count', 'satisfied', 'unsatisfied')
