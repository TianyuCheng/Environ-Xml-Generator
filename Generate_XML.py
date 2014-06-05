#!/usr/bin/env python

# import regular expression
import os, re

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

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

    # mkdir if directory not found
    if not os.path.exists("./xmls"):
        print "xmls directory not found; try generating iit"
        os.makedirs("./xmls")

    print "you are trying to generate", worksheets[option], "xml"
    print "-----------------------------------------------------"
    return option

# ================= xml generators ======================

def generate_regions(reader):
    entries = reader.read_worksheet(1)
    root = Element("regions")
    for entry in entries:
        node = SubElement(root, "region")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "name", get_spreadsheet_data(entry, "name"))
        generate_simple_tag(node, "initials", get_spreadsheet_data(entry, "initials"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "environ", get_spreadsheet_data(entry, "environ"))
        generate_simple_tag(node, "economy", get_spreadsheet_data(entry, "economy"))

        generate_simple_tag(node, "bases", get_spreadsheet_data(entry, "bases", "( )"), {}, process_dict_xml, "base", "active", "x", "y")
        generate_simple_tag(node, "events", get_spreadsheet_data(entry, "events", "( )"), {}, process_dict_xml, "event", "x", "y")

    # print prettify(root)
    file_handle = file("xmls/regions.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_bases(reader):
    entries = reader.read_worksheet(2)
    root = Element("bases")
    for entry in entries:
        node = SubElement(root, "base")

        generate_simple_tag(node, "key", get_spreadsheet_data(entry, "key"))
        generate_simple_tag(node, "title", get_spreadsheet_data(entry, "title"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "image", get_spreadsheet_data(entry, "image"))
        generate_simple_tag(node, "reference", get_spreadsheet_data(entry, "reference"))
        generate_simple_tag(node, "model_name", get_spreadsheet_data(entry, "model_name"))

        generate_simple_tag(node, "costs", get_spreadsheet_data(entry, "costs", "( )"), {}, process_list_xml, "cost")
        generate_simple_tag(node, "effects", get_spreadsheet_data(entry, "effects", "( )"), {}, process_list_xml, "effect")
        generate_simple_tag(node, "upgrades", get_spreadsheet_data(entry, "upgrades", "( )"), {}, process_list_xml, "upgrade")

    print prettify(root)
    file_handle = file("xmls/bases.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_events(reader):
    entries = reader.read_worksheet(3)
    root = Element("events")
    for entry in entries:
        node = SubElement(root, "event")

        generate_simple_tag(node, "key", get_spreadsheet_data(entry, "key"))
        generate_simple_tag(node, "title", get_spreadsheet_data(entry, "title"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "image", get_spreadsheet_data(entry, "image"))
        generate_simple_tag(node, "reference", get_spreadsheet_data(entry, "reference"))

        generate_simple_tag(node, "upgrades", get_spreadsheet_data(entry, "upgrades", "( )"), {}, process_list_xml, "upgrade")
        generate_simple_tag(node, "effects", get_spreadsheet_data(entry, "effects", "( )"), {}, process_list_xml, "effect")
        generate_simple_tag(node, "probabilities", get_spreadsheet_data(entry, "probabilities", "( )"), {}, process_list_xml, "probability")

    print prettify(root)
    file_handle = file("xmls/probabilities.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_upgrades(reader):
    entries = reader.read_worksheet(4)

def generate_costs(reader):
    entries = reader.read_worksheet(5)

def generate_effects(reader):
    entries = reader.read_worksheet(6)

def generate_probabilities(reader):
    entries = reader.read_worksheet(7)

def generate_range_conditions(reader):
    entries = reader.read_worksheet(8)

def generate_prereq_conditions(reader):
    entries = reader.read_worksheet(9)


# ================ helper methods ====================

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_spreadsheet_data(entry, key, default_value = ' '):

    # check key existence
    if key not in entry.custom:
        return default_value
    
    # fetch the value and ensure that the value is not None
    text = entry.custom[key].text
    return text if text is not None else default_value

def generate_simple_tag(parent, tag, value, attrs = {}, callback = None, child_tag = None, *args):
    # create the tag
    node = SubElement(parent, tag) 

    # processing the value with callback function
    if callback is not None:
        callback(node, value, child_tag, *args)
    else:
        node.text = value

    # process the attributes
    for key, value in attrs.iteritems():
        node.set(key, str(value))

    return node

def process_dict_xml(parent, value, tag, *args):
    # key:( ... )

    patterns = re.compile("(.+?)\s*:\s*(\(.+?\)),*")
    groups = patterns.findall(value)

    for group in groups:
        attrs = eval(group[1])
        generate_simple_tag(parent, tag, group[0], dict(zip(args, attrs)))

def process_list_xml(parent, value, tag, *args):
    # ( ... ) 

    patterns = re.compile("\((.+?)\)")
    groups = patterns.findall(value)

    nodes = groups[0].split(",")
    for node in nodes:
        generate_simple_tag(parent, tag, node)
