#!/usr/bin/env python

# append current path to syspath
import os, sys, re
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from Classes import *

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

feeds = dict()

#######################################################################
#                    spreadsheet data manipulation                    #
#######################################################################
def get_spreadsheet_data(entry, tag):
    """@todo: Docstring for get_spreadsheet_data.

    :entry: @todo
    :tag: @todo
    :returns: @todo

    """
    entry = entry.custom[tag]
    return entry.text if entry is not None else None

#######################################################################
#               parse information from the spreadsheet                #
#######################################################################
def parse_list(text, pattern = ','):
    """@todo: Docstring for parse_list.

    :text: raw string input, separated with comma
    :returns: a list of strings
    """
    if text is None:
        return []
    return text.split(pattern)

def parse_dict(text, options):
    """@todo: Docstring for parse_dict.

    :text: raw string input, separated with comma
    :returns: a dictionary
    """
    if text is None:
        return {}
    pattern = re.compile('(.+?):\((.+?)\),{0,1}')
    groups = pattern.findall(text)
    ret = dict( (item[0], dict((key, value) for key, value in zip(options, item[1].split(',')))) for item in groups)
    # print groups, "=>", ret
    return ret

def parse_dict2(text, options):
    """@todo: Docstring for parse_dict.

    :text: raw string input, separated with comma
    :returns: a dictionary
    """
    if text is None:
        return {}
    pattern = re.compile('(.+?):(.+?),{0,1}')
    groups = pattern.findall(text)
    ret = dict( (item[0], dict((key, value) for key, value in zip(options, item[1]))) for item in groups)
    return ret

#######################################################################
#                  helper functions to generate tags                  #
#######################################################################
def generate_tag_with_attrs(parent, tag, text, attribs = dict()):
    """@todo: Docstring for generate_tag_with_attrs.
    :parent: parent tag
    :tag: tag name
    :text:
    :**attrs: dictionary containing attributs
    :returns: @todo
    """
    # check the sanity of parent tag
    if parent is None:
        print "Parent is None"
        return

    # check the sanity of the tag name
    if tag is None:
        print "tag name is None"
        return

    if text is None:
        text = ' '
    # generate the tag
    node = SubElement(parent, tag)
    node.text = str(text)

    # setting up attribs
    for key, value in attribs.iteritems():
        node.set(str(key), str(value))

    return node

def generate_tag_list(parent, plural, singular, text, process_func, attribs = []):
    node = SubElement(parent, plural)
    ret = process_func(text, attribs)
    if isinstance(ret, dict):
        items = sorted(ret, key = lambda key : int(key[1:]))
        if len(items) > 0 and isinstance(items[0], dict):
            items = sorted(items, key = lambda key : ret[key]['state'], reverse = True)
        for key in items:
            generate_tag_with_attrs(node, singular, key, ret[key])
        return node
    else:
        for item in ret:
            generate_tag_with_attrs(node, singular, item)
        return node

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    ret = reparsed.toprettyxml(indent="  ")
    # print ret 
    return ret

#######################################################################
#                           XML Generation                            #
#######################################################################
def generate_regions(reader, feed):
    """@todo: Docstring for generate_regions.

    :feed: @todo
    :returns: @todo
    """
    entries = reader.read_worksheet(feed)
    root = Element('regions')
    for entry in entries:
        node = SubElement(root, 'region')
        generate_tag_with_attrs(node, 'id', get_spreadsheet_data(entry, 'id'))
        generate_tag_with_attrs(node, 'initials', get_spreadsheet_data(entry, 'initials'))
        generate_tag_with_attrs(node, 'name', get_spreadsheet_data(entry, 'name'))
        generate_tag_with_attrs(node, 'description', get_spreadsheet_data(entry, 'description'))
        generate_tag_with_attrs(node, 'image', get_spreadsheet_data(entry, 'image'))
        generate_tag_with_attrs(node, 'reference', get_spreadsheet_data(entry, 'reference'))
        # generate_tag_with_attrs(node, 'environ', get_spreadsheet_data(entry, 'environ'))
        # generate_tag_with_attrs(node, 'economy', get_spreadsheet_data(entry, 'economy'))
        
        score_node = SubElement(node, 'scores')
        generate_tag_with_attrs(score_node, 'score', 'EN', { "amount" : get_spreadsheet_data(entry, 'environ') })
        generate_tag_with_attrs(score_node, 'score', 'EC', { "amount" : get_spreadsheet_data(entry, 'economy') })

        generate_tag_with_attrs(node, 'cost', get_spreadsheet_data(entry, 'cost'))

        generate_tag_list(node, 'bases', 'base', get_spreadsheet_data(entry, 'bases'), parse_dict, ['active', 'x', 'y'])
        generate_tag_list(node, 'events', 'event', get_spreadsheet_data(entry, 'events'), parse_dict, ['x', 'y'])
    return root

def generate_bases(reader, feed):
    """@todo: Docstring for generate_regions.

    :feed: @todo
    :returns: @todo
    """
    entries = reader.read_worksheet(feed)
    root = Element('bases')
    for entry in entries:
        node = SubElement(root, 'base')
        generate_tag_with_attrs(node, 'key', get_spreadsheet_data(entry, 'key'))
        generate_tag_with_attrs(node, 'title', get_spreadsheet_data(entry, 'title'))
        generate_tag_with_attrs(node, 'description', get_spreadsheet_data(entry, 'description'))
        generate_tag_with_attrs(node, 'image', get_spreadsheet_data(entry, 'image'))
        generate_tag_with_attrs(node, 'model', get_spreadsheet_data(entry, 'model'))
        generate_tag_with_attrs(node, 'reward', get_spreadsheet_data(entry, 'reward'))

        generate_tag_list(node, 'tags', 'tag', get_spreadsheet_data(entry, 'tags'), parse_list, ',')
        generate_tag_list(node, 'upgrades', 'upgrade', get_spreadsheet_data(entry, 'upgrades'), parse_dict2,['state'] )
    return root

def generate_upgrades(reader, feed):
    """@todo: Docstring for generate_upgrades.

    :reader: @todo
    :feed: @todo
    :returns: @todo
    """
    entries = reader.read_worksheet(feed)
    root = Element('upgrades')
    for entry in entries:
        node = SubElement(root, 'upgrade')
        generate_tag_with_attrs(node, 'key', get_spreadsheet_data(entry, 'key'))
        generate_tag_with_attrs(node, 'title', get_spreadsheet_data(entry, 'title'))
        generate_tag_with_attrs(node, 'description', get_spreadsheet_data(entry, 'description'))
        generate_tag_with_attrs(node, 'image', get_spreadsheet_data(entry, 'image'))
        generate_tag_with_attrs(node, 'model', get_spreadsheet_data(entry, 'model'))
        generate_tag_with_attrs(node, 'icon', get_spreadsheet_data(entry, 'icon'))
        generate_tag_with_attrs(node, 'reference', get_spreadsheet_data(entry, 'reference'))
        generate_tag_with_attrs(node, 'time', get_spreadsheet_data(entry, 'time'))
        generate_tag_with_attrs(node, 'repurchasable_times', get_spreadsheet_data(entry, 'repurchasabletimes'))
        generate_tag_with_attrs(node, 'revertible_times', get_spreadsheet_data(entry, 'revertibletimes'))
        generate_tag_list(node, 'tags', 'tag', get_spreadsheet_data(entry, 'tags'), parse_list, ',')

        # generate costs
        costs = get_spreadsheet_data(entry, 'costs')
        costs_node = SubElement(node, 'costs')
        if costs is not None:
            for item in costs.split('\n'):
                effect = Effect(item.strip())
                generate_tag_with_attrs(costs_node, 'cost', effect.getId())

        # # generate probability
        # probs = get_spreadsheet_data(entry, 'prereqs')
        # probs_node = SubElement(node, 'probabilities')
        # if probs is not None:
        #     for item in probs.split(','):
        #         probability = Probability(item.strip())
        #         generate_tag_with_attrs(probs_node, 'probability', probability.getId())

        # generate prereqs
        prereqs = get_spreadsheet_data(entry, 'prereqs')
        prereqs_node = SubElement(node, 'prereqs')
        if prereqs is not None:
            for item in prereqs.split(','):
                prereq  = Prereq(item.strip())
                generate_tag_with_attrs(prereqs_node, 'prereq', prereq.getId())

        # generate effects
        effects = get_spreadsheet_data(entry, 'effects')
        effects_node = SubElement(node, 'effects')
        if effects is not None:
            for item in effects.split('\n'):
                effect = Effect(item.strip())
                generate_tag_with_attrs(effects_node, 'effect', effect.getId())
    return root


def generate_events(reader, feed):
    """@todo: Docstring for generate_upgrades.

    :reader: @todo
    :feed: @todo
    :returns: @todo
    """
    entries = reader.read_worksheet(feed)
    root = Element('events')
    for entry in entries:
        node = SubElement(root, 'event')
        generate_tag_with_attrs(node, 'key', get_spreadsheet_data(entry, 'key'))
        generate_tag_with_attrs(node, 'title', get_spreadsheet_data(entry, 'title'))
        generate_tag_with_attrs(node, 'description', get_spreadsheet_data(entry, 'description'))
        generate_tag_with_attrs(node, 'image', get_spreadsheet_data(entry, 'image'))
        generate_tag_with_attrs(node, 'model', get_spreadsheet_data(entry, 'model'))
        generate_tag_with_attrs(node, 'reference', get_spreadsheet_data(entry, 'reference'))
        generate_tag_with_attrs(node, 'duration', get_spreadsheet_data(entry, 'duration'))
        generate_tag_list(node, 'tags', 'tag', get_spreadsheet_data(entry, 'tags'), parse_list, ',')

        # generate prereqs
        prereqs = get_spreadsheet_data(entry, 'prereqs')
        prereqs_node = SubElement(node, 'prereqs')
        if prereqs is not None:
            for item in prereqs.split(','):
                prereq  = Prereq(item.strip())
                generate_tag_with_attrs(prereqs_node, 'prereq', prereq.getId())

        # generate probability
        probs = get_spreadsheet_data(entry, 'probability')
        probs_node = SubElement(node, 'probabilities')
        if probs is not None:
            for item in probs.split(','):
                probability = Probability(item.strip())
                generate_tag_with_attrs(probs_node, 'probability', probability.getId())

        # generate effects
        effects = get_spreadsheet_data(entry, 'effects')
        effects_node = SubElement(node, 'effects')
        if effects is not None:
            for item in effects.split('\n'):
                effect = Effect(item.strip())
                generate_tag_with_attrs(effects_node, 'effect', effect.getId())
    return root

def generate_tags(reader, feed):
    """@todo: Docstring for generate_regions.

    :feed: @todo
    :returns: @todo
    """
    entries = reader.read_worksheet(feed)
    root = Element('tags')
    for entry in entries:
        node = SubElement(root, 'tag')
        generate_tag_with_attrs(node, 'key', get_spreadsheet_data(entry, 'key'))
        generate_tag_with_attrs(node, 'title', get_spreadsheet_data(entry, 'title'))
    return root
#######################################################################
#                            main function                            #
#######################################################################
if __name__ == '__main__':

    # set up username or use the default account
    if len(sys.argv) >= 2:
        username = sys.argv[1]
    else:
        username = "skysource.tony@gmail.com"

    # set up GoogleSpreadSheetReader
    reader = SpreadsheetReader(username, "EnvironNodesInfo.gsheet")
    feeds = reader.get_worsksheet_feeds(lambda s : s.split(' ')[0])
    
    print "Here are the worksheets available"
    for key, value in feeds.iteritems():
        print key, " => ", value

    with open('xmls/regions.xml', 'w') as f:
        f.write(prettify(generate_regions(reader, feeds['Regions'])))
    with open('xmls/bases.xml', 'w') as f:
        f.write(prettify(generate_bases(reader, feeds['Bases'])))
    with open('xmls/upgrades.xml', 'w') as f:
        f.write(prettify(generate_upgrades(reader, feeds['Upgrades'])))
    with open('xmls/tags.xml', 'w') as f:
        f.write(prettify(generate_tags(reader, feeds['Tags'])))
    with open('xmls/events.xml', 'w') as f:
        f.write(prettify(generate_events(reader, feeds['Events'])))
    with open('xmls/probabilities.xml', 'w') as f:
        f.write(Probability.rootToXml() )
    with open('xmls/effects.xml', 'w') as f:
        f.write(Effect.rootToXml() )

    # print prettify(generate_regions(reader, feeds['Regions']))
    # print prettify(generate_bases(reader, feeds['Bases']))
    # print prettify(generate_upgrades(reader, feeds['Upgrades']))
    # print prettify(generate_tags(reader, feeds['Tags']))
    # print prettify(generate_events(reader, feeds['Events']))
    # print Probability.rootToXml() 
    # print Effect.rootToXml() 
