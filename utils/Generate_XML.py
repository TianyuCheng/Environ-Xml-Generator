# import regular expression
import os, re

from Check_XML import *

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

def duplicate_check(value):
    global duplicates
    return value if value not in duplicates else duplicates[value]

def duplicate_node(entry, tag):
    key = get_spreadsheet_data(entry, tag)
    return key != duplicate_check(key)

# ================= xml generators ======================

def generate_syntax(reader, feed):
    print "there's no need to generate syntax xml"

def generate_regions(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("regions")
    for entry in entries:
        if (duplicate_node(entry, "id")):
            continue

        node = SubElement(root, "region")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "name", get_spreadsheet_data(entry, "name"))
        generate_simple_tag(node, "initials", get_spreadsheet_data(entry, "initials"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "environ", get_spreadsheet_data(entry, "environ"))
        generate_simple_tag(node, "economy", get_spreadsheet_data(entry, "economy"))

        generate_simple_tag(node, "bases", get_spreadsheet_data(entry, "bases", "( )"), {}, process_dict_xml, "base", "active", "x", "y")
        generate_simple_tag(node, "events", get_spreadsheet_data(entry, "events", "( )"), {}, process_dict_xml, "event", "x", "y")

    print prettify(root)
    file_handle = file("xmls/regions.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_bases(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("bases")
    for entry in entries:
        if (duplicate_node(entry, "key")):
            continue

        node = SubElement(root, "base")

        generate_simple_tag(node, "key", get_spreadsheet_data(entry, "key"))
        generate_simple_tag(node, "title", get_spreadsheet_data(entry, "title"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "image", get_spreadsheet_data(entry, "image"))
        generate_simple_tag(node, "prefab_name", get_spreadsheet_data(entry, "prefab_name"))
        generate_simple_tag(node, "model_name", get_spreadsheet_data(entry, "model_name"))
        generate_simple_tag(node, "reference", get_spreadsheet_data(entry, "reference"))

        generate_simple_tag(node, "costs", get_spreadsheet_data(entry, "costs", "( )"), {}, process_list_xml, "cost")
        generate_simple_tag(node, "effects", get_spreadsheet_data(entry, "effects", "( )"), {}, process_list_xml, "effect")
        generate_simple_tag(node, "upgrades", get_spreadsheet_data(entry, "upgrades", "( )"), {}, process_list_xml, "upgrade")

    print prettify(root)
    file_handle = file("xmls/bases.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_events(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("events")
    for entry in entries:
        if (duplicate_node(entry, "key")):
            continue

        node = SubElement(root, "event")

        generate_simple_tag(node, "key", get_spreadsheet_data(entry, "key"))
        generate_simple_tag(node, "title", get_spreadsheet_data(entry, "title"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "image", get_spreadsheet_data(entry, "image"))
        generate_simple_tag(node, "prefab_name", get_spreadsheet_data(entry, "prefab_name"))
        generate_simple_tag(node, "model_name", get_spreadsheet_data(entry, "model_name"))
        generate_simple_tag(node, "reference", get_spreadsheet_data(entry, "reference"))

        generate_simple_tag(node, "upgrades", get_spreadsheet_data(entry, "upgrades", "( )"), {}, process_list_xml, "upgrade")
        generate_simple_tag(node, "effects", get_spreadsheet_data(entry, "effects", "( )"), {}, process_list_xml, "effect")
        # generate_simple_tag(node, "probabilities", get_spreadsheet_data(entry, "probabilities", "( )"), {}, process_list_xml, "probability")
        generate_simple_tag(node, "range_conditions", get_spreadsheet_data(entry, "rangeconditions", "( )"), {}, process_list_xml, "range_condition")
        generate_simple_tag(node, "prereq_conditions", get_spreadsheet_data(entry, "prereqconditions", "( )"), {}, process_list_xml, "prereq_condition")

    print prettify(root)
    file_handle = file("xmls/events.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_upgrades(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("upgrades")
    for entry in entries:
        if (duplicate_node(entry, "key")):
            continue

        node = SubElement(root, "upgrade")

        generate_simple_tag(node, "key", get_spreadsheet_data(entry, "key"))
        generate_simple_tag(node, "title", get_spreadsheet_data(entry, "title"))
        generate_simple_tag(node, "description", get_spreadsheet_data(entry, "description"))
        generate_simple_tag(node, "image", get_spreadsheet_data(entry, "image"))
        generate_simple_tag(node, "reference", get_spreadsheet_data(entry, "reference"))
        generate_simple_tag(node, "category", get_spreadsheet_data(entry, "category", "0"))

        generate_simple_tag(node, "costs", get_spreadsheet_data(entry, "costs", "( )"), {}, process_list_xml, "cost")
        generate_simple_tag(node, "effects", get_spreadsheet_data(entry, "effects", "( )"), {}, process_list_xml, "effect")
        # generate_simple_tag(node, "probabilities", get_spreadsheet_data(entry, "probabilities", "( )"), {}, process_list_xml, "probability")
        generate_simple_tag(node, "range_conditions", get_spreadsheet_data(entry, "rangeconditions", "( )"), {}, process_list_xml, "range_condition")
        generate_simple_tag(node, "prereq_conditions", get_spreadsheet_data(entry, "prereqconditions", "( )"), {}, process_list_xml, "prereq_condition")

    print prettify(root)
    file_handle = file("xmls/upgrades.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_costs(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("costs")
    for entry in entries:
        if (duplicate_node(entry, "id")):
            continue

        node = SubElement(root, "cost")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "duration", get_spreadsheet_data(entry, "duration", "0"))
        generate_simple_tag(node, "amount", get_spreadsheet_data(entry, "amount", "0"))

        generate_simple_tag(node, "range_conditions", get_spreadsheet_data(entry, "rangeconditions", "( )"), {}, process_list_xml, "range_condition")
        generate_simple_tag(node, "prereq_conditions", get_spreadsheet_data(entry, "prereqconditions", "( )"), {}, process_list_xml, "prereq_condition")

    print prettify(root)
    file_handle = file("xmls/costs.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_effects(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("effects")
    for entry in entries:
        if (duplicate_node(entry, "id")):
            continue

        node = SubElement(root, "effect")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "score", get_spreadsheet_data(entry, "score", "0"))
        generate_simple_tag(node, "duration", get_spreadsheet_data(entry, "duration", "0"))
        generate_simple_tag(node, "area", get_spreadsheet_data(entry, "area", "0"))
        generate_simple_tag(node, "amount", get_spreadsheet_data(entry, "amount", "0"))

    print prettify(root)
    file_handle = file("xmls/effects.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_probabilities(reader, feed):
    print "No need to generate probabilities now"
    # entries = reader.read_worksheet(feed)
    # root = Element("probabilities")
    # for entry in entries:
    #     if (duplicate_node(entry, "id")):
    #         continue
    #
    #     node = SubElement(root, "probability")
    #
    #     generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
    #
    #     generate_simple_tag(node, "range_conditions", get_spreadsheet_data(entry, "rangeconditions", "( )"), {}, process_list_xml, "range_condition")
    #     generate_simple_tag(node, "prereq_conditions", get_spreadsheet_data(entry, "prereqconditions", "( )"), {}, process_list_xml, "range_condition")
    #
    # print prettify(root)
    # file_handle = file("xmls/probabilities.xml", "w")
    # file_handle.write(prettify(root))
    # file_handle.close()

def generate_ranges(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("range_conditions")
    for entry in entries:
        if (duplicate_node(entry, "id")):
            continue

        node = SubElement(root, "range_condition")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "score", get_spreadsheet_data(entry, "score", "0"))
        generate_simple_tag(node, "low", get_spreadsheet_data(entry, "low", "0"))
        generate_simple_tag(node, "high", get_spreadsheet_data(entry, "high", "0"))
        generate_simple_tag(node, "multiplier", get_spreadsheet_data(entry, "multiplier", "0"))

    print prettify(root)
    file_handle = file("xmls/range_conditions.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()

def generate_prereqs(reader, feed):
    entries = reader.read_worksheet(feed)
    root = Element("prereq_conditions")
    for entry in entries:
        if (duplicate_node(entry, "id")):
            continue

        node = SubElement(root, "prereq_condition")

        generate_simple_tag(node, "id", get_spreadsheet_data(entry, "id"))
        generate_simple_tag(node, "keys", get_spreadsheet_data(entry, "keys", "( )"), {}, process_list_xml, "key")
        generate_simple_tag(node, "count", get_spreadsheet_data(entry, "low", "0"))
        generate_simple_tag(node, "satisfied", get_spreadsheet_data(entry, "satisfied", "0"))
        generate_simple_tag(node, "unsatisfied", get_spreadsheet_data(entry, "unsatisfied", "0"))

    print prettify(root)
    file_handle = file("xmls/prereq_conditions.xml", "w")
    file_handle.write(prettify(root))
    file_handle.close()


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
        node.text = duplicate_check(value)

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
