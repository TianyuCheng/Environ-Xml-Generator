import re 
from collections import OrderedDict

# helper methods
def to_list(value):
    patterns = re.compile("\((.+?)\)")
    groups = patterns.findall(value)

    nodes = groups[0].split(",")
    return nodes

def to_dict(value, formats):
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
             "title" : "dummy title", \
             "bases" : "( )", \
             "events" : "( )", \
           }

# this is the format for regions worksheet
regions_format = OrderedDict([  ("id", "tag"), \
                                ("initials", "tag"), \
                                ("name", "tag"), \
                                ("description", "tag"), \
                                ("image", "tag"), \
                                ("reference", "tag"), \
                                ("environ", "tag"), \
                                ("economy", "tag"), \
                                ("bases", [to_dict, "base", OrderedDict([\
                                    ("active", "attribute"), \
                                    ("x", "attribute"), \
                                    ("y", "attribute") \
                                    ]) \
                                ]),
                                ("events", [to_dict, "event", OrderedDict([\
                                    ("x", "attribute"), \
                                    ("y", "attribute") \
                                    ]) \
                                ]),
                                ("cost", "tag")
                                ])

# this is the format for tags worksheet
tags_format = OrderedDict([ ("key", "tag"), \
                            ("title", "tag") ])
