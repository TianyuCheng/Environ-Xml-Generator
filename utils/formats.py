import re 
from collections import OrderedDict

# helper methods
def to_list(value):
    patterns = re.compile("\((.+?)\)")
    groups = patterns.findall(value)

    nodes = groups[0].split(",")
    return nodes

def from_list(value, formats):
    nodes = to_list(value)

    ret = dict()
    for item in nodes:
        ret[item] = {}
    return ret
        
def from_dict(value, formats):
    patterns = re.compile("(.+?)\s*:\s*(\(.+?\)),*")
    groups = patterns.findall(value)

    ret = dict(groups)

    for key in ret.iterkeys():
        ret[key] = dict(zip(formats.keys(), to_list(ret[key])))
    return ret


# default values
defaults = { "effects" : "( )", \
             "upgrades" : "( )", \
             "tags" : "( )", \
             "title" : " ", \
             "model" : " ", \
             "reference" : " ", \
             "category" : "-1", \
             "image" : " ", \
             "time" : "-1", \
             "duration" : "-1", \
             "amount" : "-1", \
             "repurchasable" : "FALSE", \
             "bases" : "( )", \
             "events" : "( )", \
             "impacts" : "( )", \
             "costs" : "( )", \
             "prereqconditionspos" : "( )", \
             "prereqconditionsneg" : "( )", \
             "prereqtagspos" : "( )", \
             "prereqtagsneg" : "( )", \
             "prereqscorespos" : "( )", \
             "prereqscoresneg" : "( )", \
             "conditions" : "( )", \
             "prereqnodes" : "( )", \
           }

"""
FORMAT
tag: simple tag, e.g. <title> Moon-based Solar Power </title>
attribute: simple attribute of the current tag, e.g. <base active="1" x="255" y="81">B1</base>
[list]: list of tags 
[0] -> callback to process the data in fetched from google spread sheet
[1] -> tag name inside the list
[2] -> format of the sub tag
"""

# this is the format for regions worksheet
region_format = OrderedDict([  ("id", "tag"), \
                                ("initials", "tag"), \
                                ("name", "tag"), \
                                ("description", "tag"), \
                                ("image", "tag"), \
                                ("reference", "tag"), \
                                ("environ", "tag"), \
                                ("economy", "tag"), \
                                ("bases", [from_dict, "base", OrderedDict([\
                                    ("active", "attribute"), \
                                    ("x", "attribute"), \
                                    ("y", "attribute") \
                                    ]) \
                                ]),
                                ("events", [from_dict, "event", OrderedDict([\
                                    ("x", "attribute"), \
                                    ("y", "attribute") \
                                    ]) \
                                ]),
                                ("cost", "tag")
                                ])

# this is the format for events worksheet
event_format = OrderedDict([ ("key", "tag"), \
                             ("title", "tag"), \
                             ("description", "tag"), \
                             ("image", "tag"), \
                             ("model", "tag"), \
                             ("reference", "tag"), \
                             ("tags", [from_list, "tag", {}]), \
                             ("prereqconditionspos", [from_list, "prereqconditionpos", {}]), \
                             ("prereqconditionsneg", [from_list, "prereqconditionneg", {}]), \
                             ("prereqtagspos", [from_list, "prereqtagpos", {}]), \
                             ("prereqtagsneg", [from_list, "prereqtagneg", {}]), \
                             ("prereqscorespos", [from_list, "prereqscorepos", {}]), \
                             ("prereqscoresneg", [from_list, "prereqscoreneg", {}]), \
                             ("effects", [from_list, "effect", {}]), \
#                             ("impacts", [from_list, "impact", {}]), \
                         ])

# this is the format for events worksheet
base_format = OrderedDict([ ("key", "tag"), \
                             ("title", "tag"), \
                             ("description", "tag"), \
                             ("image", "tag"), \
                             ("model", "tag"), \
                             ("reference", "tag"), \
                             ("tags", [from_list, "tag", {}]), \
                             ("upgrades", [from_list, "upgrade", {}]), \
                             ("costs", [from_list, "cost", {}]), \
                             ("impacts", [from_list, "impacts", {}]), \
                         ])


# this is the format for events worksheet
upgrade_format = OrderedDict([ ("key", "tag"), \
                               ("title", "tag"), \
                               ("description", "tag"), \
                               ("image", "tag"), \
                               ("model", "tag"), \
                               ("reference", "tag"), \
                               ("time", "tag"), \
                               ("tags", [from_list, "tag", {}]), \
                               ("category", "tag"), \
                               ("repurchasable", "tag"), \
                               ("costs", [from_list, "cost", {}]), \
                               ("effects", [from_list, "effect", {}]), \
#                               ("impacts", [from_list, "impacts", {}]), \
                               ("conditions", [from_list, "condition", {}]), \
                            ])

# this is the format for tags worksheet
tag_format = OrderedDict([ ("key", "tag"), \
                            ("title", "tag") ])


# this is the format for costs worksheet
cost_format = OrderedDict([ ("key", "tag"), \
                            ("duration", "tag"), \
                            ("amount", "tag"), \
                            ("prereqnodes", [from_list, "prereqnode", {}]), \
                        ])

# this is the format for effects worksheet
effect_format = OrderedDict([ ("key", "tag"), \
                              ("prereqtagspos", [from_list, "prereqtagpos", {}]), \
                              ("prereqtagsneg", [from_list, "prereqtagneg", {}]), \
                              ("prereqscorespos", [from_list, "prereqscorepos", {}]), \
                              ("prereqscoresneg", [from_list, "prereqscoreneg", {}]), \
                           ])
