#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import re
from schlib import *

def readStyle(style):
    style_units={}

    for filename in [f for f in os.listdir(os.path.join(os.getcwd(), 'symbol_generator_data','single_comps',style)) if re.match(r'.*\.lib', f)]:
        style_units[os.path.splitext(os.path.basename(filename))[0]]=SchLib(filename)
        print('STYLE-TEMPLATE: ', os.path.splitext(os.path.basename(filename))[0], 'from', filename)
    
    return style_units

def readLIBDefinition(libdef_fn):
    libdef = open(libdef_fn, "r")
    component_templates = []
    comp = {}
    unit = {}
    for line_in in libdef:
        line = line_in.strip()
        
        # filter out comments
        if line.startswith('#'):
            continue
        else:
            if line.startswith('$ENDCMP'):
                if len(unit) > 0:
                    comp['units'].append(unit)
                #print('ADD TEMPLATE:')
                #for c in comp:
                #    print(c, ':', comp[c])
                component_templates.append(comp)
            
            # parse '$CMP <NAME>'
            match = re.match(r'\$CMP\s*(\w+)\s*', line, re.IGNORECASE)
            if match:
                comp = {}
                comp['name'] = match.group(1)
                comp['units'] = []
            
            # parse '$ALIAS <AL1> <AL2> ...'
            match = re.match(r'\$ALIAS\s*((\w+)\s*)+\s*', line, re.IGNORECASE)
            if match:
                comp['alias'] = match.groups()
            
            # parse '$FPLIST <FP1> <FP2> ...'
            match = re.match(r'\$FPLIST\s*(([^\s]+)\s*)+\s*', line, re.IGNORECASE)
            if match:
                comp['fplist'] = match.groups()
            
            # parse '?UNITS <COUNT> <TEMPLATE_NAME>'
            match = re.match(r'\?UNITS\s+(\d+)\s+(\w+)\s*', line, re.IGNORECASE)
            if match:
                if len(unit) > 0:
                    comp['units'].append(unit)
                unit = {}
                unit['template'] = match.group(2).lower()
                unit['count'] = int(match.group(1))
            unit['type'] = 'unit'
            
            # parse '?UNIT <TEMPLATE_NAME>'
            match = re.match(r'\?UNIT\s+(\w+)\s*', line, re.IGNORECASE)
            if match:
                if len(unit) > 0:
                    comp['units'].append(unit)
                unit = {}
                unit['template'] = match.group(1)
                unit['count'] = 1
                unit['type'] = 'unit'
                unit['pins'] = []
            
            # parse '?PWR'
            match = re.match(r'\?PWR\s*', line, re.IGNORECASE)
            if match:
                if len(unit) > 0:
                    comp['units'].append(unit)
                unit = {}
                unit['template'] = 'POWER'
                unit['count'] = 1
                unit['type'] = 'power'
                unit['pins'] = []
            
            # parse '<PIN> <NAME> <PIN> <NAME> ...'
            match = re.match(r'(\d+\s+[\.\-\_\w\~]+\s*)+\s*', line, re.IGNORECASE)
            if match:
                g = 1;
                pp = []
                pattern = re.compile(r'(\d+)\s+([\.\-\_\w\~]+)\s*')
                for (pin, name) in re.findall(pattern, line):
                    p = {}
                    p['pin'] = int(pin)
                    p['name'] = name
                    pp.append(p)
                    g = g + 2;
                
                if ~('pins' in unit):
                    unit['pins'] = []
                unit['pins'].append(pp)
    return component_templates


def main(libfilename, libdef_files, style):
    
    # read in style files
    print('READING STYLE ', style)
    style_units=readStyle(style)
    print(style_units)

    # parse library definition files in libdef_files
    
    component_templates=[]
    for libdef_fn in libdef_files:
        print('READING COMPONENT DEFINITION FILE ', libdef_fn)
        component_templates.append(readLIBDefinition(libdef_fn))

    #open library
    print ('OPENING LIBRARY FILE ', libfilename)
    lib = SchLib(libfilename)


    # finally save the lib
    print('SAVING LIBRARY FILE ', libfilename)
    lib.save()
    










if __name__ == "__main__":
    # execute only if run as a script
    main("test.lib", [ os.path.join(os.getcwd(), 'symbol_generator_data', 'lib_def', 'logic_gates.txt')],  "ANSI")