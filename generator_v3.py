#!/usr/bin/env python

# append current path to syspath
import os, sys, re
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from re import compile

# import xml utils
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

#######################################################################
#                          global variables                           #
#######################################################################
keys = dict()
regions = dict()
bases = dict()
upgrades = dict()
events = dict()
tags = dict()
prereqs = dict()
costs = dict()
effects = dict()

#######################################################################
#                    spreadsheet data manipulation                    #
#######################################################################
def get_spreadsheet_data(entry, tag):
    try:
        entry = entry.custom[tag]
        return entry.text if entry is not None else None
    except KeyError:
        print "[Error]", tag, "has not been found in the entry"
    return None

#######################################################################
#                          utility functions                          #
#######################################################################
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    ret = reparsed.toprettyxml(indent="  ")
    return ret

def replace_variable(var):
    if var == 'PCC':
        return 'PC'
    if var == '$C':
        return '$'
    return var

def create_subselement(parent, tag, text, attribs = {}):
    node = SubElement(parent, tag, attribs)
    node.text = text
    return node
    
#######################################################################
#                               classes                               #
#######################################################################
class Info(object):

    def __init__(self):
        self.info = dict()

    def set(self, key, value):
        if key is None:
            # print "[Error] key is None"
            return
        if value is None:
            self.info[key] = ""
            # print "[Warning] value is None for", key
            return

        self.info[key] = value

    def get(self, key):
        if key is None:
            print "The key is None"
        elif key not in self.info:
            print "The key", key, "is not in the information"
        else:
            return self.info[key]
        return None

    def set_tags(self, tags):
        self.tags = []
        if tags is not None:
            self.tags = compile("\s*,?\s*").split(tags.strip())

    def set_prereqs(self, prereqs):
        self.prereqs = []

        if prereqs is None:
            return

        groups = compile("\s*,?\s*").split(prereqs.strip())
        for group in groups:
            self.prereqs.append(Prerequisite(group))

        # for prereq in self.prereqs:
        #     print prereq

    def set_costs(self, costs):
        if costs is None:
            return

        self.costs = Cost(costs)
        # print self.costs

    def set_effects(self, effects):

        self.effects = []

        if effects is None:
            return

        groups = compile("\s*").split(effects.strip())
        for group in groups:
            self.effects.append(Effect(group))

        # for effect in self.effects:
        #     print effect


class Region(Info):

    def __init__(self, _id, initials, name):
        super(Region, self).__init__()
        self.id = _id
        self.initials = initials
        self.name = name

    def set_initial_values(self, pairs):
        self.initial_values = dict()
        if pairs is not None:
            pairs = compile("\s*,?\s+").split(pairs.strip())
            try:
                for pair in pairs:
                    key, value = pair.split(":")
                    # population as an exception
                    if key == 'PO':
                        amount, rate = value[1:-1].split(",")
                        self.initial_values[key] = { "amount": amount, "rate": rate}
                    else:
                        self.initial_values[key] = value
            except ValueError:
                print "too many values to unpack in region:", self.name, value
            # print self.initial_values

    def set_bases(self, bases):
        self.bases = dict()
        if bases is not None:
            pairs = compile('(\w+):\((.+?)\),?\s*').findall(bases.strip())
            attrs = ["state", "x", "y"]
            try:
                for pair in pairs:
                    key = pair[0]
                    attributes = dict(zip(attrs, pair[1].split(",")))
                    self.bases[key] = attributes
            except ValueError:
                print "[Error] too many values to unpack in region:", self.name, value
            # print self.bases

    def set_events(self, events):
        self.events = dict()
        if events is not None:
            pairs = compile('(\w+):\((.+?)\),?\s*').findall(events.strip())
            attrs = ["x", "y"]
            try:
                for pair in pairs:
                    key = pair[0]
                    attributes = dict(zip(attrs, pair[1].split(",")))
                    self.events[key] = attributes
            except ValueError:
                print "[Error] too many values to unpack in region:", self.name, value
                raise
            # print self.events

    def toXML(self):
        node = Element("region")
        create_subselement(node, "id", self.id)
        create_subselement(node, "initials", self.initials)
        create_subselement(node, "name", self.name)
        create_subselement(node, "description", self.get("description"))
        create_subselement(node, "image", self.get("image"))

        # initial values
        initial_values_node = SubElement(node, "initial_values")
        for key, value in self.initial_values.iteritems():
            if isinstance(value, dict):
                create_subselement(initial_values_node, "value", key, value)
            else:
                create_subselement(initial_values_node, "value", key, {"amount":value})

        # unique conditions
        effects_node = SubElement(node, "unique_conditions")
        for effect in self.effects:
            create_subselement(effects_node, "effect", effect.key)

        # bases
        bases = sorted(self.bases, key = lambda key : int(key[1:]))
        bases = sorted(bases, key = lambda key : self.bases[key]['state'], reverse = True)
        bases_node = SubElement(node, "bases")
        for key in bases:
            attribs = self.bases[key]
            create_subselement(bases_node, "base", key, {"state":attribs["state"], "x":attribs["x"], "y":attribs["y"]})

        # events
        events = sorted(self.events, key = lambda key : int(key[1:]))
        events_node = SubElement(node, "events")
        for key in events:
            attribs = self.events[key]
            create_subselement(events_node, "event", key, {"x":attribs["x"], "y":attribs["y"]})
        
        # tags
        tags_node = SubElement(node, "tags")
        for tag in self.tags:
            create_subselement(tags_node, "tag", tag)

        return node

class Base(Info):

    def __init__(self, key, title):
        super(Base, self).__init__()
        self.title = title
        self.key = key 
        self.upgrades = dict()

    def set_initial_impacts(self, impacts):
        if impacts is not None:
            pairs = compile('(\w+)\((.+?)\),?\s*').findall(impacts.strip())
            for pair in pairs:
                key = pair[0]
                environment, economy = pair[1].split(",")
                # find the base attributes in the regions
                try:
                    base_attribs = regions[key].bases[self.key]
                    base_attribs['EC'] = economy
                    base_attribs['EN'] = environment
                    base_attribs['multipliers'] = "1"
                except KeyError:
                    print self.key, "has not been found in region", key
        # else:
        #     print "[Warning] input for initial conditions is none in", self.title

    def set_multipliers(self, multipliers):
        if multipliers is not None:
            pairs = compile('(\w+)\((.+?)\),?\s*').findall(multipliers.strip())
            for pair in pairs:
                key = pair[0]
                # find the base attributes in the regions
                try:
                    base_attribs = regions[key].bases[self.key]
                    base_attribs['multipliers'] = pair[1]
                except KeyError:
                    print self.key, "has not been found in region", key
        # else:
        #     print "[Warning] input for multipliers is none in", self.title

    def toXML(self):
        node = Element("base")
        create_subselement(node, "key", self.key)
        create_subselement(node, "title", self.title)
        create_subselement(node, "description", self.get("description"))
        create_subselement(node, "image", self.get("image"))
        create_subselement(node, "model", self.get("model"))
        create_subselement(node, "reference", self.get("reference"))
        # TODO: to finishi this part later

class Upgrade(Info):

    def __init__(self, key, title):
        super(Upgrade, self).__init__()
        self.title = title
        self.key = key 

    def set_base(self, key, state):
        bases[key].upgrades[self.key] = { "state" : state }

class Event(Info):

    def __init__(self, key, title):
        super(Event, self).__init__()
        self.title = title
        self.key = key 

class Tag(object):

    def __init__(self, key, title):
        super(Tag, self).__init__()
        self.title = title
        self.key = key 

class Prerequisite(Info):

    def __init__(self, prereqs):
        super(Prerequisite, self).__init__()
        fmts = ['!', '>', '<']
        for fmt in fmts:
            index = prereqs.find(fmt)
            if index < 0:
                continue

            if fmt == '!':
                self.relation = -1
                self.key = prereqs[index + 1:]
                self.type = 'Node'
            elif fmt == '>':
                self.relation = 1
                self.key = prereqs[:index]
                self.amount = prereqs[index + 1:]
                self.type = 'Score'
            elif fmt == '<':
                self.relation = -1
                self.key = prereqs[:index]
                self.amount = prereqs[index + 1:]
                self.type = 'Score'
            self.__save__();
            return

        # normal situation
        self.relation = 1
        self.key = prereqs
        self.amount = 0
        self.type = 'Node'
        self.__save__();

    def __save__(self):
        key = str(self)
        if key in prereqs:
            self.key = prereqs[key].key
        else:
            self.key = "Q%d" % (len(prereqs) + 1)
            prereqs[key] = self

    def __str__(self):
        if self.type == 'Node':
            return self.type + '|' + self.key + '|' + str(self.relation)
        else:
            return self.type + '|' + self.key + '|' + str(self.relation) + '|' + str(self.amount)

class Probability(Info):

    def __init__(self, probability):
        super(Probability, self).__init__()

class Cost(Info):

    def __init__(self, cost):
        super(Cost, self).__init__()
        pairs = compile("\s*,?\s*").split(cost)
        try:
            for pair in pairs:
                key, value = pair.split(":")
                self.set(replace_variable(key), value)
        except ValueError:
            print "[Error] too many things to unpack in cost"

        self.__save__()

    def __save__(self):
        key = str(self)
        if key in costs:
            self.key = costs[key].key
        else:
            self.key = "C%d" % (len(costs) + 1)
            costs[key] = self

    def __str__(self):
        return str(self.info)

class Effect(object):

    def __init__(self, effect):
        super(Effect, self).__init__()
        # print effect
        pairs = compile("(\S+?=>)?(\S+?)\((\S+?)\)").findall(effect)
        if len(pairs) > 1:
            print "Input for more than one pair"
            raise
            print "Not able to parse effect"
            raise
        pairs = pairs[0]
        # factor(...)
        self.factor = pairs[0][:-2]
        params = pairs[1].split(",")
        if len(params) == 1:
            self.duration = "0"
            self.amount = params[0]
        elif len(params) == 2:
            self.duration = params[0]
            self.amount = params[1]
        else:
            print "Effect format error"
        self.__save__()

    def __save__(self):
        key = str(self)
        if key in effects:
            self.key = effects[key].key
        else:
            self.key = "F%d" % (len(effects) + 1)
            effects[key] = self

    def __str__(self):
        return self.factor + "|" + str(self.duration) + "|" + str(self.amount)

#######################################################################
#                              generator                              #
#######################################################################
def init_keys(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            keys[key] = get_spreadsheet_data(entry, "value")

def init_tags(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            tags[key] = get_spreadsheet_data(entry, "title")

def init_regions(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        _id = get_spreadsheet_data(entry, "id")
        if _id is not None:
            initials = get_spreadsheet_data(entry, "initials")
            name = get_spreadsheet_data(entry, "name")
            region = Region(_id, initials, name)
            region.set("description", get_spreadsheet_data(entry, "description"))
            region.set("image", get_spreadsheet_data(entry, "image"))
            region.set_initial_values(get_spreadsheet_data(entry, "initialvalues"))
            region.set_effects(get_spreadsheet_data(entry, "uniquecondition"))
            region.set_bases(get_spreadsheet_data(entry, "bases"))
            region.set_events(get_spreadsheet_data(entry, "events"))
            region.set_tags(get_spreadsheet_data(entry, "tags"))
            regions[initials] = region

def init_bases(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            base = Base(key, get_spreadsheet_data(entry, "title"))
            base.set("description", get_spreadsheet_data(entry, "description"))
            base.set("image", get_spreadsheet_data(entry, "image"))
            base.set("model", get_spreadsheet_data(entry, "model"))
            base.set("reference", get_spreadsheet_data(entry, "reference"))
            base.set_initial_impacts(get_spreadsheet_data(entry, "initialimpacts"))
            base.set_multipliers(get_spreadsheet_data(entry, "multipliers"))
            base.set_tags(get_spreadsheet_data(entry, "tags"))
            bases[key] = base

def init_upgrades(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            upgrade = Upgrade(key, get_spreadsheet_data(entry, "title"))
            upgrade.set("order", get_spreadsheet_data(entry, "order"))
            upgrade.set("description", get_spreadsheet_data(entry, "description"))
            upgrade.set("image", get_spreadsheet_data(entry, "image"))
            upgrade.set("model", get_spreadsheet_data(entry, "model"))
            upgrade.set("icon", get_spreadsheet_data(entry, "icon"))
            upgrade.set("reference", get_spreadsheet_data(entry, "reference"))
            upgrade.set("build_time", get_spreadsheet_data(entry, "buildtime"))
            upgrade.set("levels", get_spreadsheet_data(entry, "levels"))
            upgrade.set("cost_multiplier", get_spreadsheet_data(entry, "costmultiplier"))
            upgrade.set("effect_multiplier", get_spreadsheet_data(entry, "effectmultiplier"))
            upgrade.set_prereqs(get_spreadsheet_data(entry, "prereqs"))
            upgrade.set_costs(get_spreadsheet_data(entry, "costs"))
            upgrade.set_effects(get_spreadsheet_data(entry, "effects"))
            upgrade.set_base(get_spreadsheet_data(entry, "base"), get_spreadsheet_data(entry, "initialstate"))
            upgrade.set_tags(get_spreadsheet_data(entry, "tags"))
            upgrades[key] = upgrade

def init_events(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            event = Event(key, get_spreadsheet_data(entry, "title"))
            event.set("description", get_spreadsheet_data(entry, "description"))
            event.set("image", get_spreadsheet_data(entry, "image"))
            event.set("model", get_spreadsheet_data(entry, "model"))
            event.set("reference", get_spreadsheet_data(entry, "reference"))
            # TODO: set prereqs
            # upgrade.set_prereqs(get_spreadsheet_data(entry, "prereqs"))
            # TODO: set probability
            # TODO: set effect
            event.set_tags(get_spreadsheet_data(entry, "tags"))
            events[key] = event


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
    reader = SpreadsheetReader(username, "EnvironNodesInfo (Matt and Peter).gsheet")
    feeds = reader.get_worsksheet_feeds(lambda s : s.split(' ')[0])
    
    print "Here are the worksheets available"
    for key, value in feeds.iteritems():
        print key, " => ", value

    init_keys(reader, feeds['Keys'])
    init_tags(reader, feeds['Tags'])
    init_regions(reader, feeds['Regions'])
    init_bases(reader, feeds['Bases'])
    init_upgrades(reader, feeds['Upgrades'])
    init_events(reader, feeds['Events'])

    # for key, value in effects.iteritems():
    #     print value.key, "\t=>\t", value
    #
    # for key, value in costs.iteritems():
    #     print value.key, "\t=>\t", value
    #
    # for key, value in prereqs.iteritems():
    #     print value.key, "\t=>\t", value

    # print keys
    # print regions
    # print bases
    # print upgrades
    # print events

    # for key, value in sorted(regions.iteritems(), key = lambda x: x[1].id):
    #     print prettify(value.toXML())

    for key, value in sorted(bases.iteritems(), key = lambda x: x[1].key):
        print prettify(value.toXML())
