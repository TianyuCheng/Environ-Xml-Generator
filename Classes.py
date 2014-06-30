import re 

# import XML api
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom

scores = ['EC', 'EN', 'AP', 'LP', 'WP', '']

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
        id_node = SubElement(node, 'id')
        id_node.text = self.id
        factor_node = SubElement(node, 'factors')
        for key, value in self.__attribs.iteritems():
            child = SubElement(factor_node, 'factor')
            child.text = key
            child.set('rel', value)
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
        for item in texts:
            separator_index = item.find(' ')
            score_name = item[:separator_index]
            amount = eval(item[separator_index:])
            if not isinstance(amount, int):
                print "Error in evaluating amount in texts", text
                return
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
        id_node = SubElement(node, 'id')
        id_node.text = self.id
        probability_node = SubElement(node, 'probability')
        probability_node.text = self.__probabilityid
        factor_node = SubElement(node, 'factors')
        for key, value in self.__attribs.iteritems():
            child = SubElement(factor_node, 'factor')
            child.text = key
            child.set('amount', str(value))
        return node

    @staticmethod
    def rootToXml():
        return prettify(effects_root)
