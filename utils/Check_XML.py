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

def check_syntax(reader, feed):
    print "No need to check duplicates in syntax"

def check_regions(reader, feed):
    print "No need to check duplicates in regions"

def check_bases(reader, feed):
    print "No need to check duplicates in bases"

def check_events(reader, feed):
    print "No need to check duplicates in events"

def check_upgrades(reader, feed):
    print "No need to check duplicates in upgrades"

def check_costs(reader, feed):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(feed)
    check_duplicates(entries, 'id', 'duration', 'amount', 'rangeconditions')

def check_effects(reader, feed):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(feed)
    check_duplicates(entries, 'id', 'score', 'duration', 'area', 'amount')

def check_probabilities(reader, feed):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(feed)
    check_duplicates(entries, 'id', 'rangeconditions', 'prereqconditions')

def check_ranges(reader, feed):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(feed)
    check_duplicates(entries, 'id', 'score', 'low', 'high', 'multiplier')

def check_prereqs(reader, feed):
    # fetch the rows of the spreadsheet
    entries = reader.read_worksheet(feed)
    check_duplicates(entries, 'id', 'keys', 'count', 'satisfied', 'unsatisfied')
