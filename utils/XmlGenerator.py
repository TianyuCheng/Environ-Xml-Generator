#!/usr/bin/env python

""" This is the second version of xml generator
    It makes use of decorator and is more resillient
    to changes
"""

from formats import *

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# generator function
def generate_xml(tag_name, formats):
    """@todo: Docstring for generate_tag.
    :tag_name: generate the tag with this name
    :formats: the generator needs to follow the formats
    :returns: @a function to generate the tags of the same kind
    """
    def generate(root, content):
        node = SubElement(root, tag_name)
        for key, value in formats.iteritems():
            # this is for simple tag without any attributes
            if value == 'tag':
                child = SubElement(node, key)
                child.text = content[key]
            # this is for tags with attributes
            elif value == 'attribute':
                node.set(key, content[key])
            # this is for list inside of this tag
            elif isinstance(value, list):
                callback = value[0]         # get callback function
                childtag = value[1]         # get child tag name
                child_format = value[2]     # get child format
                # generate tag function
                generate_child = generate_xml(childtag, child_format)
                # parse information from raw string
                child_infos = callback(content[key], child_format)

                curr_node = SubElement(node, key)
                for ckey, cvalue in child_infos.iteritems(): 
                    subnode = generate_child(curr_node, cvalue)     # generate the tag
                    subnode.text = ckey                             # set the tag text
                    # print ckey, cvalue

        return node # return the generated node for other uses

    return generate

def fill_with_default(entry):
    ret = dict()
    for key, value in entry.custom.iteritems():
        if value is None or value.text is None:
            ret[key] = defaults[key] if key in defaults else " "
        else:
            ret[key] = value.text
    return ret 
