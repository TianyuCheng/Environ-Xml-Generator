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
probabilities = dict()
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
        self.costs = None
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
            fx = Effect(group)
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
            _impacts[key] = { "EC":environment, "EN":economy }

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
        bases[key].upgrades[self.key] = { "state" : state }

    def toXML(self):
        node = Element("upgrade")
        create_subselement(node, "key", self.key)
        create_subselement(node, "title", self.title)
        # if self.get("description") is not None:
            # create_subselement(node, "description", self.get("description"))
        # else:
        create_subselement(node, "description", "Lorem ipsum")
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
        create_subselement(node, "image", self.get("image"))
        create_subselement(node, "model", self.get("model"))
        create_subselement(node, "reference", self.get("reference"))
        create_subselement(node, "duration", self.get("duration"))

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
        # print pairs[0], "=>",  pairs[1]
        self.targets = pairs[0][:-2].split("&")
        self.key = pairs[1]
        params = pairs[2].split(",")
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
            self.id = effects[key].id
        else:
            self.id = "F%d" % (len(effects) + 1)
            effects[key] = self

    def __str__(self):
        return str(self.targets) + "|" + self.key + "|" + str(self.duration) + "|" + str(self.amount)

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
            event.set("duration", get_spreadsheet_data(entry, "duration"))
            event.set_prereqs(get_spreadsheet_data(entry, "prereqs"))
            event.set_probabilities(get_spreadsheet_data(entry, "probability"))
            event.set_effects(get_spreadsheet_data(entry, "effects"))
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

    root_tags = Element("tags")
    for key, value in sorted(tags.iteritems(), key = lambda x: int(x[1].key[1:])):
    # for key, value in tags.iteritems():
        root_tags.append(value.toXML())
    with open('xmls/tags.xml', 'w') as f:
        f.write(prettify(root_tags))

    root_effects = Element("effects")
    for key, value in sorted(effects.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in effects.iteritems():
        root_effects.append(value.toXML())
    with open('xmls/effects.xml', 'w') as f:
        f.write(prettify(root_effects))

    root_costs = Element("costs")
    for key, value in sorted(costs.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in costs.iteritems():
        root_costs.append(value.toXML())
    with open('xmls/costs.xml', 'w') as f:
        f.write(prettify(root_costs))

    root_prereqs = Element("prereqs")
    for key, value in sorted(prereqs.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in prereqs.iteritems():
        root_prereqs.append(value.toXML())
    with open('xmls/prereqs.xml', 'w') as f:
        f.write(prettify(root_prereqs))

    root_probabilities = Element("probabilities")
    for key, value in sorted(probabilities.iteritems(), key = lambda x: int(x[1].id[1:])):
    # for key, value in probabilities.iteritems():
        root_probabilities.append(value.toXML())
    with open('xmls/probabilities.xml', 'w') as f:
        f.write(prettify(root_probabilities))

    root_regions = Element("regions")
    for key, value in sorted(regions.iteritems(), key = lambda x: x[1].id):
        root_regions.append(value.toXML())
    with open('xmls/regions.xml', 'w') as f:
        f.write(prettify(root_regions))

    root_bases = Element("bases")
    for key, value in sorted(bases.iteritems(), key = lambda x: x[1].key):
        root_bases.append(value.toXML())
    with open('xmls/bases.xml', 'w') as f:
        f.write(prettify(root_bases))

    root_events = Element("events")
    for key, value in sorted(events.iteritems(), key = lambda x: x[1].key):
        root_events.append(value.toXML())
    with open('xmls/events.xml', 'w') as f:
        f.write(prettify(root_events))

    root_upgrades = Element("upgrades")
    upgrades = sorted(upgrades.iteritems(), key = lambda x: int(x[1].get("order")))
    upgrades = sorted(upgrades, key = lambda x: int( x[1].key[1:x[1].key.find('-')]) )
    for key, value in upgrades:
        root_upgrades.append(value.toXML())
    with open('xmls/upgrades.xml', 'w') as f:
        f.write(prettify(root_upgrades))
