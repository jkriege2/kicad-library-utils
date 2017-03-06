# -*- coding: utf-8 -*-

import sys
sys.path.append("..\..\common")

from rule import *

#this should go to separate file
def pinElectricalTypeToStr(pinEType):
    pinMap={"I":"INPUT",\
    "O":"OUTPUT",\
    "B":"BIDI",\
    "T":"TRISTATE",\
    "P":"PASSIVE",\
    "U":"UNSPECIFIED",\
    "W":"POWER INPUT",\
    "w":"POWER OUTPUT",\
    "C":"OPEN COLLECTOR",\
    "E":"OPEN EMITTER",\
    "N":"NOT CONNECTED"}
    if pinEType in pinMap.keys():
        return pinMap[pinEType]
    else:
        return "INVALID"

def pinTypeToStr(pinType):
    pinMap={"I":"INVERTED",\
    "C":"CLOCK",\
    "CI":"INVERTED CLOCK",\
    "L":"INPUT LOW",\
    "CL":"CLOCK LOW",\
    "V":"OUTPUT LOW",\
    "F":"FALLING EDGE CLOCK",\
    "X":"NON LOGIC"}
    if pinType in pinMap.keys():
        return pinMap[pinType]
    else:
        return "INVALID"
        
def backgroundFillToStr(bgFill):
    bgMap={
    "F":"FOREGROUND",
    "f":"BACKGROUND",
    "N":"TRANSPARENT"}
    if bgFill in bgMap.keys():
        return bgMap[bgFill]
    else:
        return "INVALID"

def positionFormater(element):
    if type(element) != type({}):
        raise Exception("input type: ",type(element),"expected dictionary, ",element)
    if(not {"posx","posy"}.issubset(element.keys())):
        raise Exception("missing keys 'posx' and 'posy' in"+str(element))
    return "@ ({0}, {1})".format(element['posx'],element['posy'])
    # return "pos [{0},{1}]".format(element['posx'],element['posy'])

class KLCRule(KLCRuleBase):
    """
    A base class to represent a KLC rule
    """

    verbosity = 0

    def __init__(self, component, name, description):
    
        KLCRuleBase.__init__(self, name, description)
        
        self.component = component
