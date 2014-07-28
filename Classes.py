import re 

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

scores = ['FUNDS', 'PC', 'EC', 'EN', 'AP', 'LP', 'WP', 'CO2', 'TECH', 'GREEN', 'GDP', 'PP', 'EQ']
nodes = ['B', 'E', 'U']

# parent nodes
probabilities_root = Element("probabilities")
effects_root = Element("effects")

# index of probabilities and effects, for index generation
probability_index = 0
effect_index = 0

probabilities = dict()
effects = dict()


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_type(key):
    if key in scores:
        return 'score'
    if key[:1] in nodes:
        return 'node'
    if key[:1] == 'T':
        return 'tag'
    return 'none'

#######################################################################
#                               Prereqs                               #
#######################################################################
class Prereq(object):
    """Docstring for Prereq. """

    def __init__(self, text):
        """@todo: to be defined1. """
        self.__xmlTag = None
        self.text = text
        # check which type
        
        self.__attribs = dict()
        
        index1 = text.find('>')
        index2 = text.find('<')
        index3 = text.find('+')
        index4 = text.find('-')
        if index1 > 0:
            key = text[:index1].strip()
            self.__attribs[key] = ('1', text[index1 + 1:].strip())
        elif index2 > 0:
            key = text[:index2].strip()
            self.__attribs[key] = ('-1', text[index2 + 1:].strip())
        elif index3 > 0:
            key = text[:index3].strip()
            self.__attribs[key] = ('1', '0')
        elif index4 > 0:
            key = text[:index4].strip()
            self.__attribs[key] = ('-1', '0')

        tostr = str(self.__attribs)
        if tostr in probabilities:
            self.id = probabilities[tostr].getId()
            self = probabilities[tostr]
        else:
            global probability_index
            probability_index += 1
            self.id = 'P%d' % probability_index
            probabilities[tostr] = self
        self.__xmlTag = self.toXmlTag()

    def getId(self):
        return self.id

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        # return str(self.__attribs)
        return self.id

    def toXmlTag(self):
        """@todo: Docstring for toXml.
        :returns: @todo
        """
        if self.__xmlTag is not None:
            return self.__xmlTag

        node = SubElement(probabilities_root, 'probability')
        key_node = SubElement(node, 'key')
        key_node.text = self.id
        factors_node = SubElement(node, 'factors')
        for key, value in self.__attribs.iteritems():
            factor_node = SubElement(factors_node, 'factor')
            factor_node.text = key
            factor_node.set('type', get_type(key))
            factor_node.set('rel', value[0])
            factor_node.set('amount', value[1])

#######################################################################
#                             Probability                             #
#######################################################################
class Probability(object):
    """docstring for Probability"""

    def __init__(self, text):
        super(Probability, self).__init__()
        self.__xmlTag = None
        self.text = text
        
        texts = [item.strip() for item in text.split('&')]
        self.__attribs = dict( (key.strip(), value.strip()) for key, value in map(lambda x : [x[:-1], x[-1:]], texts))

        tostr = str(self.__attribs)
        if tostr in probabilities:
            self.id = probabilities[tostr].getId()
            self = probabilities[tostr]
        else:
            global probability_index
            probability_index += 1
            self.id = 'P%d' % probability_index
            probabilities[tostr] = self
        self.__xmlTag = self.toXmlTag()
    
    def getId(self):
        return self.id

    def __str__(self):
        """@todo: Docstring for __str__.
        :returns: @todo

        """
        # return str(self.__attribs)
        return self.id
 
    def toXmlTag(self):
        """@todo: Docstring for toXml.
        :returns: @todo
        """
        if self.__xmlTag is not None:
            return self.__xmlTag

        node = SubElement(probabilities_root, 'probability')
        id_node = SubElement(node, 'key')
        id_node.text = self.id
        factor_node = SubElement(node, 'factors')
        for key, value in self.__attribs.iteritems():
            child = SubElement(factor_node, 'factor')
            child.text = key
            child.set('type', get_type(key))
            child.set('rel', '1' if value == '+' else '-1')
            child.set('amount', '0')
        return node
    
    @staticmethod
    def rootToXml():
        return prettify(probabilities_root)


#######################################################################
#                               Effects                               #
#######################################################################

class Effect(object):

    """Docstring for Effect. """

    def __init__(self, text):
        """@todo: to be defined1. """
        super(Effect, self).__init__()
        self.__xmlTag = None

        groups = text.split('=>')
        # we do not have prereq weights
        if len(groups) == 1:
            self.__probability = None
            self.__probabilityid = ''
            texts = groups[0]
        # we have prereq weights
        elif len(groups) == 2:
            self.__probability = Probability(groups[0])
            # self.__probabilityId = '1'
            self.__probabilityid = self.__probability.getId()
            texts = groups[1]
        else:
            print "input error on Texts: ", text
            return

        self.__attribs = dict() 
        texts = [item.strip() for item in texts.split(',')]
        # print texts
        for item in texts:
            separator_index = item.find('+')
            if separator_index == -1:
                separator_index = item.find('-')
            score_name = item[:separator_index].strip()
            amount = eval(item[separator_index:])
            # if not isinstance(amount, int) or not isinstance(amount, float):
            #     print "Error in evaluating amount in texts", text
            #     return
            self.__attribs[score_name] = amount

        tostr = str(self)
        if tostr in effects:
            self.id = effects[tostr].getId()
            self = effects[tostr]
        else:
            global effect_index
            effect_index += 1
            self.id = 'F%d' % effect_index
            effects[tostr] = self

        self.__xmlTag = self.toXmlTag()

    def __str__(self):
        """@todo: Docstring for __str__.

        :arg1: @todo
        :returns: @todo

        """
        return "%s => %s" % (str(self.__probability), str(self.__attribs))

    def getId(self):
        """@todo: Docstring for getId.
        :returns: @todo
        """
        return self.id

    def toXmlTag(self):
        """@todo: Docstring for toXml.
        :returns: @todo
        """
        if self.__xmlTag is not None:
            return self.__xmlTag

        node = SubElement(effects_root, 'effect')
        id_node = SubElement(node, 'key')
        id_node.text = self.id
        probability_node = SubElement(node, 'probability')
        probability_node.text = self.__probabilityid
        factor_node = SubElement(node, 'scores')
        for key, value in self.__attribs.iteritems():
            child = SubElement(factor_node, 'score')
            child.text = key
            child.set('amount', str(value))
        return node

    @staticmethod
    def rootToXml():
        return prettify(effects_root)
