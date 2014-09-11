#!/usr/bin/env python

# append current path to syspath
import os, sys, re, getopt
lib_path = os.path.abspath('./utils')
sys.path.append(lib_path)

# import utils
from GoogleReader import SpreadsheetReader
from re import compile

# import xml utils
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

# import json utils
from json import dumps

# import console printing commands
from sys import stdout, stderr
from collections import deque

# import debug tools
import traceback

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
probabilities = dict()
costs = dict()
effects = dict()

targets = dict()
nodes = dict()

# json export variables
json_root = dict()

#######################################################################
#                            Configuration                            #
#######################################################################
verbose = False
username = "skysource.tony@gmail.com"

def parse_args():
    global verbose
    global username
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hvu:", ["help", "username=", "verbose"])
    except getopt.GetoptError:
        print 'generator.py --username=<username> [--verbose]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'generator.py --username=<username> [--verbose]'
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-v", "--verbose"):
            verbose = True

#######################################################################
#                    spreadsheet data manipulation                    #
#######################################################################
def get_spreadsheet_data(entry, tag):
    try:
        entry = entry.custom[tag]
        return entry.text if entry is not None else None
    except KeyError:
        print "[Error]", "<%s>" % tag, "has not been found in the entry"
        print "An error occured in", "[%s]" % str(traceback.extract_stack(limit=2)[-2][2])
        print "Exit abnormally"
        sys.exit(-1)
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
        self.effects = []

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
        self.costs = None
        if costs is None:
            return

        self.costs = Cost(costs)
        # print self.costs

    def set_effects(self, effects, duration):

        if effects is None or effects is "":
            return

        groups = compile("\s*").split(effects.strip())
        for group in groups:
            group = group.strip()
            if group is not "" and group is not None:
                fx = Effect(group, duration)
                self.effects.append(fx)
            # print fx.id, ">>>", group
        # print '====>'

        # for effect in self.effects:
        #     print effect

    def set_probabilities(self, probabilities):

        self.probabilities = []

        if probabilities is None:
            return

        groups = compile("\s*").split(probabilities.strip())
        for group in groups:
            self.probabilities.append(Probability(group))

        # for probability in self.probabilities:
        #     print probability

class Region(Info):

    def __init__(self, _id, initials, name):
        super(Region, self).__init__()
        self.id = _id
        self.initials = initials
        self.name = name
        self.growth_rate = "0"

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
                        # self.initial_values[key] = { "amount": amount, "rate": rate}
                        self.initial_values[key] = amount;
                        self.growth_rate = rate
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
        create_subselement(node, "growth_rate", self.growth_rate)

        # initial values
        initial_values_node = SubElement(node, "scores")
        for key, value in self.initial_values.iteritems():
            if isinstance(value, dict):
                create_subselement(initial_values_node, "score", key, value)
            else:
                create_subselement(initial_values_node, "score", key, {"amount":value})

        # unique conditions
        effects_node = SubElement(node, "unique_conditions")
        for effect in self.effects:
            create_subselement(effects_node, "effect", effect.id)

        # bases
        bases = sorted(self.bases, key = lambda key : int(key[1:]))
        bases = sorted(bases, key = lambda key : self.bases[key]['state'], reverse = True)
        bases_node = SubElement(node, "bases")
        for key in bases:
            attribs = self.bases[key]
            base_node = create_subselement(bases_node, "base", "", {"state":attribs["state"], "x":attribs["x"], "y":attribs["y"], "key": key, "multiplier": attribs["multiplier"]})
            for key, value in attribs["impacts"].iteritems():
                impact_node = create_subselement(base_node, "impact", key, {"amount": str(value)})

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
        if impacts is None:
            impacts = ""

        _impacts = dict()
        pairs = compile('(\w+)\((.+?)\),?\s*').findall(impacts.strip())
        for pair in pairs:
            key = pair[0]
            environment, economy = pair[1].split(",")
            _impacts[key] = { "EC":economy, "EN": environment }

        for initials, region in regions.iteritems():
            try:
                if initials is "W":
                    continue
                base_attribs = region.bases[self.key]
                if initials in _impacts:
                    base_attribs['impacts'] = { "EC": _impacts[initials]["EC"], "EN": _impacts[initials]["EN"] }
                else:
                    base_attribs['impacts'] = { "EC": "0", "EN": "0" }
            except KeyError:
                print "[Error] cannot find base", self.key, " in the region", initials

    def set_multipliers(self, multipliers):
        if multipliers is None:
            multipliers = ""

        pairs = compile('(\w+)\((.+?)\),?\s*').findall(multipliers.strip())

        multipliers = dict()
        for pair in pairs:
            key = pair[0]
            multipliers[key] = pair[1]

        for initials, region in regions.iteritems():
            try:
                if initials is "W":
                    continue
                base_attribs = region.bases[self.key]
                if initials in multipliers:
                    base_attribs['multiplier'] = multipliers[initials]
                else:
                    base_attribs['multiplier'] = "1"
            except KeyError:
                print "[Error] cannot find base", self.key, " in the region", initials

    def toXML(self):
        node = Element("base")
        create_subselement(node, "key", self.key)
        create_subselement(node, "title", self.title)
        create_subselement(node, "description", self.get("description"))
        create_subselement(node, "image", self.get("image"))
        create_subselement(node, "model", self.get("model"))
        create_subselement(node, "reference", self.get("reference"))
        # TODO: add upgrades

        # upgrades
        _upgrades = sorted(self.upgrades, key = lambda key : key[1:])
        _upgrades = sorted(_upgrades, key = lambda key : int(key[key.find('-') + 1:]))
        _upgrades = sorted(_upgrades, key = lambda key : self.upgrades[key]['state'], reverse = True)
        upgrades_node = SubElement(node, "upgrades")
        for key in _upgrades:
            attribs = self.upgrades[key]
            upgrade_node = create_subselement(upgrades_node, "upgrade", key, {"state":attribs["state"]})

        # tags
        tags_node = SubElement(node, "tags")
        for tag in self.tags:
            create_subselement(tags_node, "tag", tag)

        return node

class Upgrade(Info):

    def __init__(self, key, title):
        super(Upgrade, self).__init__()
        self.title = title
        self.key = key 

    def set_base(self, key, state):
        self.set("base", key)
        bases[key].upgrades[self.key] = { "state" : state }

    def toXML(self):
        node = Element("upgrade")
        create_subselement(node, "key", self.key)
        create_subselement(node, "title", self.title)
        create_subselement(node, "description", self.get("description"))
        create_subselement(node, "effects_description", self.get("effects_description"))
        create_subselement(node, "image", self.get("image"))
        create_subselement(node, "model", self.get("model"))
        create_subselement(node, "icon", self.get("icon"))
        create_subselement(node, "reference", self.get("reference"))
        create_subselement(node, "build_time", self.get("build_time"))

        create_subselement(node, "levels", self.get("levels"))
        multipliers_node = SubElement(node, "multipliers")
        create_subselement(multipliers_node, "cost", self.get("cost_multiplier"))
        create_subselement(multipliers_node, "effect", self.get("effect_multiplier"))

        # create costs and effects
        costs_node = SubElement(node, "costs")
        if self.costs is not None:
            create_subselement(costs_node, "cost", self.costs.id)

        effects_node = SubElement(node, "effects")
        for effect in self.effects:
            create_subselement(effects_node, "effect", effect.id)

        prereqs_node = SubElement(node, "prereqs")
        for prereq in self.prereqs:
            create_subselement(prereqs_node, "prereq", prereq.id)

        # tags
        tags_node = SubElement(node, "tags")
        for tag in self.tags:
            create_subselement(tags_node, "tag", tag)

        return node

class Event(Info):

    def __init__(self, key, title):
        super(Event, self).__init__()
        self.title = title
        self.key = key 

    def toXML(self):
        node = Element("event")
        create_subselement(node, "key", self.key)
        create_subselement(node, "title", self.title)
        create_subselement(node, "description", self.get("description"))
        create_subselement(node, "effects_description", self.get("effects_description"))
        create_subselement(node, "image", self.get("image"))
        create_subselement(node, "model", self.get("model"))
        create_subselement(node, "reference", self.get("reference"))
        create_subselement(node, "duration", self.get("duration"))
        create_subselement(node, "scope", self.get("scope"))

        # tags
        tags_node = SubElement(node, "tags")
        for tag in self.tags:
            create_subselement(tags_node, "tag", tag)

        # prereqs
        _prereqs = sorted(self.prereqs, key = lambda key : int(key.id[1:]))
        prereqs_node = SubElement(node, "prereqs")
        for key in _prereqs:
            prereq_node = create_subselement(prereqs_node, "prereq", key.id)

        # probabilities
        probabilities_node = SubElement(node, "probabilities")
        for probability in self.probabilities:
            create_subselement(probabilities_node, "probability", probability.id)

        # effects
        effects_node = SubElement(node, "effects")
        for effect in self.effects:
            create_subselement(effects_node, "effect", effect.id)

        return node

class Tag(object):

    def __init__(self, key, title):
        super(Tag, self).__init__()
        self.title = title
        self.key = key 

    def toXML(self):
        node = Element("tag")
        key_node = create_subselement(node, "key", self.key)
        title_node = create_subselement(node, "title", self.title)
        return node

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
                self.type = 'node'
            elif fmt == '>':
                self.relation = 1
                self.key = prereqs[:index]
                self.amount = prereqs[index + 1:]
                self.type = 'score'
            elif fmt == '<':
                self.relation = -1
                self.key = prereqs[:index]
                self.amount = prereqs[index + 1:]
                self.type = 'score'
            self.__save__();
            return

        # normal situation
        self.relation = 1
        self.key = prereqs
        self.amount = 0
        self.type = 'node'
        self.__save__();

    def __save__(self):
        key = str(self)
        if key in prereqs:
            self.id = prereqs[key].id
        else:
            self.id = "Q%d" % (len(prereqs) + 1)
            prereqs[key] = self

    def __str__(self):
        if self.type == 'node':
            return self.type + '|' + self.key + '|' + str(self.relation)
        else:
            return self.type + '|' + self.key + '|' + str(self.relation) + '|' + str(self.amount)

    def toXML(self):
        node = Element("prereq")
        key_node = create_subselement(node, "key", self.id)
        factors_node = create_subselement(node, "factors", "")
        if self.type == "node":
            target_node = create_subselement(factors_node, "factor", self.key, {"relation": str(self.relation), "amount": "0", "type": self.type})
        else:
            target_node = create_subselement(factors_node, "factor", self.key, {"relation": str(self.relation), "amount": str(self.amount), "type": self.type})
        return node

class Probability(Info):

    def __init__(self, probability):
        super(Probability, self).__init__()
        if probability is None:
            return

        self.items = dict()
        items = probability.split('&')
        for item in items:
            if item[-1:] == '-':
                key = item[:-1]
                relation = -1
            elif item[-1:] == '+':
                key = item[:-1]
                relation = 1
            else:
                key = item
                relation = 1

            if key in keys or key == 'PC' or key == '$':
                self.items[key] = {"relation": relation, "type": "score"}
            else:
                self.items[key] = {"relation": relation, "type": "node"}

        self.__save__()

    def __save__(self):
        key = str(self)
        if key in probabilities:
            self.id = probabilities[key].id
        else:
            self.id = "P%d" % (len(probabilities) + 1)
            probabilities[key] = self

    def __str__(self):
        return str(self.items)

    def toXML(self):
        node = Element("probability")
        key_node = create_subselement(node, "key", self.id)
        factors_node = create_subselement(node, "factors", "")
        for key, value in self.items.iteritems():
            factor_node = create_subselement(factors_node, "factor", key, {"type": value["type"], "relation": str(value["relation"]), "amount": "0"})
            # subkey_node = create_subselement(factor_node, "key", key)
            # relation_node = create_subselement(factor_node, "relation", str(value["relation"]))
        return node

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
            self.id = costs[key].id
        else:
            self.id = "C%d" % (len(costs) + 1)
            costs[key] = self

    def __str__(self):
        return str(self.info)

    def toXML(self):
        node = Element("cost")
        key_node = create_subselement(node, "key", self.id)
        scores_node = create_subselement(node, "scores", "")
        for key, value in self.info.iteritems():
            create_subselement(scores_node, "score", key, {"amount":value})
        return node

class Effect(object):

    def __init__(self, effect, duration):
        super(Effect, self).__init__()
        self.__parse__(effect, duration)
        self.__save__()

    def __parse__(self, effect, duration):
        pairs = compile("(\S+?=>)?(\S+?)\((\S+?)\)").findall(effect)
        if len(pairs) > 1 or len(pairs) == 0:
            print "Input for more than one pair"
            print "Not able to parse effect"
            print "effects input:", effect
            raise
        pairs = pairs[0]
        # factor(...)
        # print pairs[0], "=>",  pairs[1]
        self.targets = pairs[0][:-2].split("&")
        self.key = pairs[1]
        self.amount = pairs[2]
        self.duration = duration

    def __save__(self):
        key = str(self)
        if key in effects:
            self.id = effects[key].id
        else:
            self.id = "F%d" % (len(effects) + 1)
            effects[key] = self

    def __str__(self):
        ret = ""
        for target in targets:
            ret += target + "&"
        return ret[:-1] + "=>(%s, %s)" % (self.duration, self.amount)
        # return str(self.targets) + "|" + self.key + "|" + str(self.duration) + "|" + str(self.amount)

    def toXML(self):
        node = Element("effect")
        key_node = create_subselement(node, "key", self.id)
        target_node = create_subselement(node, "targets", "")
        duration_node = create_subselement(node, "duration", str(self.duration))
        for target in self.targets:
            if target.strip():
                create_subselement(target_node, "target", target)
        scores_node = SubElement(node, "scores")
        create_subselement(scores_node, "score", str(self.key), {"amount":str(self.amount)})
        return node

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
        key = get_spreadsheet_data(entry, "key").strip()
        if key is not None:
            tags[key] = Tag(key, get_spreadsheet_data(entry, "title").strip())
            # tags[key] = get_spreadsheet_data(entry, "title").strip()

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
            region.set_effects(get_spreadsheet_data(entry, "uniquecondition"), "0")
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
            # upgrade.set("description", strcat(get_spreadsheet_data(entry, "description"), get_spreadsheet_data(entry, "effectsdescription")))
            upgrade.set('description', get_spreadsheet_data(entry, "description"))
            upgrade.set('effects_description', get_spreadsheet_data(entry, "effectsdescription"))
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
            upgrade.set_effects(get_spreadsheet_data(entry, "immediateeffects"), "0")
            upgrade.set_effects(get_spreadsheet_data(entry, "effectsovertime"), get_spreadsheet_data(entry, "effectsduration"))
            upgrade.set_base(get_spreadsheet_data(entry, "base"), get_spreadsheet_data(entry, "initialstate"))
            upgrade.set_tags(get_spreadsheet_data(entry, "tags"))
            upgrades[key] = upgrade

def init_events(reader, feed):
    entries = reader.read_worksheet(feed)
    for entry in entries:
        key = get_spreadsheet_data(entry, "key")
        if key is not None:
            event = Event(key, get_spreadsheet_data(entry, "title"))
            # event.set("description", strcat(get_spreadsheet_data(entry, "description"), get_spreadsheet_data(entry, "effectsdescription")))
            event.set('description', get_spreadsheet_data(entry, "description"))
            event.set('effects_description', get_spreadsheet_data(entry, "effectsdescription"))
            event.set("image", get_spreadsheet_data(entry, "image"))
            event.set("model", get_spreadsheet_data(entry, "model"))
            event.set("reference", get_spreadsheet_data(entry, "reference"))
            event.set("duration", get_spreadsheet_data(entry, "duration"))
            event.set("scope", get_spreadsheet_data(entry, "scope"))
            event.set_prereqs(get_spreadsheet_data(entry, "prereqs"))
            event.set_probabilities(get_spreadsheet_data(entry, "probability"))
            # event.set_effects(get_spreadsheet_data(entry, "effects"))
            event.set_effects(get_spreadsheet_data(entry, "immediateeffects"), "0")
            event.set_effects(get_spreadsheet_data(entry, "effectsovertime"), get_spreadsheet_data(entry, "effectsduration"))
            event.set_tags(get_spreadsheet_data(entry, "tags"))
            events[key] = event

#######################################################################
#                              Generator                              #
#######################################################################
def generate_xml():
    # check directory
    directory = "./xmls"
    if not os.path.exists(directory):
        os.makedirs(directory)

    root_tags = Element("tags")
    for key, value in sorted(tags.iteritems(), key = lambda x: int(x[1].key[1:])):
    # for key, value in tags.iteritems():
        root_tags.append(value.toXML())
    with open('xmls/tags.xml', 'w') as f:
        f.write(prettify(root_tags).encode("utf-8"))

    root_effects = Element("effects")
    for key, value in sorted(effects.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in effects.iteritems():
        root_effects.append(value.toXML())
    with open('xmls/effects.xml', 'w') as f:
        f.write(prettify(root_effects).encode("utf-8"))

    root_costs = Element("costs")
    for key, value in sorted(costs.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in costs.iteritems():
        root_costs.append(value.toXML())
    with open('xmls/costs.xml', 'w') as f:
        f.write(prettify(root_costs).encode("utf-8"))

    root_prereqs = Element("prereqs")
    for key, value in sorted(prereqs.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in prereqs.iteritems():
        root_prereqs.append(value.toXML())
    with open('xmls/prereqs.xml', 'w') as f:
        f.write(prettify(root_prereqs).encode("utf-8"))

    root_probabilities = Element("probabilities")
    for key, value in sorted(probabilities.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in probabilities.iteritems():
        root_probabilities.append(value.toXML())
    with open('xmls/probabilities.xml', 'w') as f:
        f.write(prettify(root_probabilities).encode("utf-8"))

    root_regions = Element("regions")
    for key, value in sorted(regions.iteritems(), key = lambda x: int(x[1].id)):
        root_regions.append(value.toXML())
    with open('xmls/regions.xml', 'w') as f:
        f.write(prettify(root_regions).encode("utf-8"))

    root_bases = Element("bases")
    for key, value in sorted(bases.iteritems(), key = lambda x: int(x[1].key[1:])):
        root_bases.append(value.toXML())
    with open('xmls/bases.xml', 'w') as f:
        f.write(prettify(root_bases).encode("utf-8"))

    root_events = Element("events")
    for key, value in sorted(events.iteritems(), key = lambda x: int(x[1].key[1:])):
        root_events.append(value.toXML())
    with open('xmls/events.xml', 'w') as f:
        f.write(prettify(root_events).encode("utf-8"))

    root_upgrades = Element("upgrades")
    _upgrades = sorted(upgrades.iteritems(), key = lambda x: int(x[1].get("order")))
    _upgrades = sorted(_upgrades, key = lambda x: int(x[1].get("base")[1:]))
    for key, value in _upgrades:
        root_upgrades.append(value.toXML())
    with open('xmls/upgrades.xml', 'w') as f:
        f.write(prettify(root_upgrades).encode("utf-8"))

def generate_json():
    # generate json for html tool
    json_root["regions"] = dict()
    json_root["events"] = dict()
    json_root["bases"] = dict()

    # generate each region's children events and bases
    json_regions = json_root["regions"]
    for initials, region in regions.iteritems():
        # region_bases = list()
        # region_events = list()
        # for base in region.bases.iterkeys():
        #     region_bases.append(base)
        # for event in region.events.iterkeys():
        #     region_events.append(event)
        # json_regions[initials] = {"bases": region_bases, "events": region_events};
        json_regions[initials] =  {"bases": region.bases, "events": region.events};

    json_bases = json_root["bases"]
    for key, base in bases.iteritems():
        json_bases[key] = base.title

    json_events = json_root["events"]
    for key, event in events.iteritems():
        json_events[key] = event.title

    with open('data.json', 'wt') as out:
        res = dumps(json_root, sort_keys=True, indent=4, separators=(',', ': '))
        out.write(res)

#######################################################################
#                          semantic checker                           #
#######################################################################
def semantic_check():
    if verbose:
        print "========================="
        print "... Semantic Checking ..."
        print "========================="

    # combine all available targets
    targets.update(bases)
    targets.update(upgrades)
    targets.update(events)
    targets.update(tags)
    targets.update(keys)

    nodes.update(bases)
    nodes.update(events)
    nodes.update(upgrades)

    for initials, region in regions.iteritems():
        check_region(region)
    if verbose:
        print ""

    for key, base in bases.iteritems():
        check_base(base)
    if verbose:
        print ""

    for key, upgrade in upgrades.iteritems():
        check_upgrade(upgrade)
    if verbose:
        print ""

    for key, event in events.iteritems():
        check_event(event)
    if verbose:
        print ""

    # # effects
    # for key, effect in effects.iteritems():
    #     check_effect(effect)

def prompt(flag, message, error_prompt):
    attr = []
    if flag:
        if verbose: # print only in verbose mode
            attr.append('32')   # green
            stdout.write('\x1b[%sm%s\x1b[0m' % (';'.join(attr), "[correct] "))
            stdout.write(message)
            stdout.write("\n")
    else:
        attr.append('31')   # red
        stderr.write('\x1b[%sm%s\x1b[0m' % (';'.join(attr), "[warning] "))
        stderr.write(message)
        stderr.write("\n")
        stderr.write('\x1b[%sm%s\x1b[0m' % (';'.join(attr), "[details] "))
        stderr.write(error_prompt)
        stderr.write("\n")

def is_number(s):
    try:
        float(s) # for int, long and float
    except ValueError:
        return False
    return True

def is_int(s):
    try:
        int(s) # for int
    except ValueError:
        return False
    return True

def check_keywords(iterable, dictionary):
    # generic keyword checker
    def checker(message):
        flag = True
        incorrects = []
        # iterate through list
        if isinstance(iterable, list):
            for item in iterable:
                if isinstance(item, str):
                    item = item.strip()
                if item:
                    if item not in dictionary:
                        incorrects.append(item)
                        flag = False
            prompt(flag, message, str(incorrects))
        # iterate through dictionary
        elif isinstance(iterable, dict):
            for key, value in iterable.iteritems():
                if isinstance(key, str):
                    key = key.strip()
                if key:
                    if key not in dictionary:
                        incorrects.append(key)
                        flag = False
            prompt(flag, message, str(incorrects))
        else:
            raise
    return checker

def check_effect(effect):
    # check target
    check_targets = check_keywords(effect.targets, targets)
    check_targets("Checking keywords in %s target" % effect.id)

    # check score of the effect
    flag = False if str(effect.key) not in keys else True
    prompt(flag, "Checking keywords in %s score" % effect.id, str(effect.key))

    flag = False if not is_number(effect.duration) else True
    prompt(flag, "Checking validity of effects duration duration of effect %s" % effect.id, str(effect.key))


# def check_cost(cost):
#     if cost is None:
#         return
#     # check score of the effect
#     for key, value in cost.info.iteritems():
#         flag = False if str(key) not in keys else True
#         prompt(flag, "Checking keywords in %s score" % cost.id, str(key))

def check_prereqs(node, path = deque([])):
    for prereq in node.prereqs:
        # score
        if prereq.type == "score":
            continue
        # node/tags
        key = prereq.key
        # check keywords
        if key not in targets:
            prompt(False, "Checking Prerequisite, not found key in targets", key)
        # ignore tags
        if key not in nodes:
            continue

        # detect a loop
        if key in path:
            path.append(key)
            prompt(False, "Checking Prerequisite, found loop", str(list(path)))
            path.pop()
            return False

        # good so far, keep going
        next_node = nodes[key]
        path.append(key)
        result = check_prereqs(next_node, path)
        path.pop()
        if not result:
            return False

    return True

def check_region(region):
    if verbose:
        print "Checking Region %s" % region.initials
    # initial values
    check_initial_values = check_keywords(region.initial_values, keys)
    check_initial_values("Checking keywords in %s initial values" % region.initials)

    # check bases
    check_bases = check_keywords(region.bases, bases)
    check_bases("Checking keywords in %s bases" % region.initials)
    for key, attribs in region.bases.iteritems():
        if not is_int(attribs['state']):
            prompt(False, "Base %s's state is not a number" % key, "state: " + attribs['state'])
        if not is_number(attribs['x']):
            prompt(False, "Base %s's location x is not a number" % key, "x: " + attribs['x'])
        if not is_number(attribs['y']):
            prompt(False, "Base %s's location y is not a number" % key, "y: " + attribs['y'])
        if not is_number(attribs['multiplier']):
            prompt(False, "Base %s's location multiplier is not a number" % key, "multiplier: " + attribs['multiplier'])
        for score, amount, in attribs["impacts"].iteritems():
            if not is_number(amount):
                prompt(False, "Base %s's impact %s is not a number" % (key, score), score + ": " + amount)

    # check events
    check_events = check_keywords(region.events, events)
    check_events("Checking keywords in %s events" % region.initials)
    for key, attribs in region.events.iteritems():
        if not is_number(attribs['x']):
            prompt(False, "Event %s's location x is not a number" % key, "x: " + attribs['x'])
        if not is_number(attribs['y']):
            prompt(False, "Event %s's location y is not a number" % key, "y: " + attribs['y'])
    
    # tags
    check_tags = check_keywords(region.tags, tags)
    check_tags("Checking keywords in %s tags" % region.initials)

    # unique conditions
    for effect in region.effects:
        check_effect(effect)

    if verbose:
        print ""

def check_base(base):
    if verbose:
        print "Checking Base [%s] %s" % (base.key, base.title)
    # tags
    check_tags = check_keywords(base.tags, tags)
    check_tags("Checking keywords in %s %s tags" % (base.key, base.title))

    # upgrades initial state
    for key, upgrade in base.upgrades.iteritems():
        if not is_int(upgrade["state"]):
            prompt(False, "Upgrades %s's initial state is not a number" % upgrade.title, upgrade['state'])
        else:
            if int(upgrade["state"]) < 0:
                prompt(False, "Upgrades %s's initial state is below 0" % upgrade.title, upgrade['state'])
    if verbose:
        print ""


def check_upgrade(upgrade):
    if verbose:
        print "Checking Upgrade [%s] %s" % (upgrade.key, upgrade.title)
    # check key and order consistency
    dash_index = upgrade.key.find("-")
    if dash_index == -1:
        prompt(False, "Upgrades %s's key does not agree with the general format U?-?" % upgrade.title, upgrade.key)
    else:
        base = upgrade.key[1:dash_index]
        _base = upgrade.get("base")[1:]
        if not is_int(base):
            prompt(False, "Upgrades %s's key is potentially corrupt" % upgrade.title, upgrade.key)
        elif not is_int(_base):
            prompt(False, "Upgrades %s's base is potentially corrupt" % upgrade.title, _base)
        else:
            if int(base) != int(_base):
                prompt(False, "Upgrades %s's base does not agree with the key, potentially corrupt" % upgrade.title, "base: " + _base + "\t key: " + upgrade.key)

    build_time = upgrade.get("build_time")
    if not is_number(build_time) or float(build_time) < 0:
        prompt(False, "Upgrades %s's build time is potentially corrupt" % upgrade.title, build_time)

    levels = upgrade.get("levels")
    if not is_int(levels) or int(levels) < 0:
        prompt(False, "Upgrades %s's levels is potentially corrupt" % upgrade.title, levels)

    cost_multiplier = upgrade.get("cost_multiplier")
    if not is_number(cost_multiplier) or float(cost_multiplier) < 0:
        prompt(False, "Upgrades %s's cost multiplier is potentially corrupt" % upgrade.title, cost_multiplier)

    effect_multiplier = upgrade.get("effect_multiplier")
    if not is_number(effect_multiplier) or float(effect_multiplier) < 0:
        prompt(False, "Upgrades %s's effect multiplier is potentially corrupt" % upgrade.title, effect_multiplier)

    check_prereqs(upgrade)

    # effects
    for effect in upgrade.effects:
        check_effect(effect)

    # costs
    # check_cost(upgrade.costs)

    # tags
    check_tags = check_keywords(upgrade.tags, tags)
    check_tags("Checking keywords in %s %s tags" % (upgrade.key, upgrade.title))

    if verbose:
        print ""

def check_event(event):
    if verbose:
        print "Checking Event [%s] %s" % (event.key, event.title)

    if not is_number(event.get("duration")):
        prompt(False, "Event %s's duration is not a number" % key, "duration: " + event.get("duration"))

    scope = event.get("scope")
    if scope is not "R" and scope is not "G":
        prompt(False, "Event %s's scope should be either G or R" % key, "scope: " + event.get("scope"))

    check_prereqs(event)

    # probabilities
    probabilities = []
    for p in event.probabilities:
        probabilities.extend(p.items.keys())
    check_probabilities = check_keywords(probabilities, targets)
    check_probabilities("Checking keywords in %s %s probabilities" % (event.key, event.title))

    # effects
    for effect in event.effects:
        check_effect(effect)

    # tags
    check_tags = check_keywords(event.tags, tags)
    check_tags("Checking keywords in %s %s tags" % (event.key, event.title))

    if verbose:
        print ""

#######################################################################
#                            main function                            #
#######################################################################
if __name__ == '__main__':
    # set up username or use the default account
    parse_args()

    # set up GoogleSpreadSheetReader
    reader = SpreadsheetReader(username, "EnvironNodesInfo (Matt and Peter).gsheet")
    feeds = reader.get_worsksheet_feeds(lambda s : s.split(' ')[0])
    
    if verbose:
        print "Here are the worksheets available"
        for key, value in feeds.iteritems():
            print key, " => ", value

    init_keys(reader, feeds['Keys'])
    init_tags(reader, feeds['Tags'])
    init_regions(reader, feeds['Regions'])
    init_bases(reader, feeds['Bases'])
    init_upgrades(reader, feeds['Upgrades'])
    init_events(reader, feeds['Events'])

    semantic_check()
    generate_xml()
    generate_json()
