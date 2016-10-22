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
    last_alias=''
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
            
            # parse '$CMP <NAME> <REFDES>'
            match = re.match(r'\$CMP\s+(\w+)\s+(\w+)\s*', line, re.IGNORECASE)
            if match:
                comp = {}
                comp['name'] = match.group(1)
                comp['ref'] = match.group(2)
                comp['text_offset'] = 10
                comp['draw_pinnumber'] = 'Y'
                comp['draw_pinname'] = 'Y'
                comp['units_locked'] = 'L'
                comp['option_flag'] = 'N'
                comp['units'] = []

            # parse '$DESC <TEXT>'
            match = re.match(r'\$DESC\s+(.*)', line, re.IGNORECASE)
            if match:
                comp['description'] = match.group(1)

            # parse '$KEYS <TEXT>'
            match = re.match(r'\$KEYS\s+(.*)', line, re.IGNORECASE)
            if match:
                comp['keys'] = match.group(1)

            # parse '$DATASHEET <TEXT>'
            match = re.match(r'\$DATASHEET\s+(.*)', line, re.IGNORECASE)
            if match:
                comp['datasheet'] = match.group(1)

            # parse '$ALIAS <AL1> <AL2> ...'
            match = re.match(r'\$ALIAS\s*(?:(\w+)\s*)+\s*', line, re.IGNORECASE)
            if match:
                if comp.get('alias', None)==None:
                    comp['alias']=[]
                for a in match.groups():
                    comp['alias'].append(a)
                    if comp.get('alias_description', None) == None: comp['alias_description'] = []
                    if comp.get('alias_keys', None) == None: comp['alias_keys'] = []
                    if comp.get('alias_datasheet', None) == None: comp['alias_datasheet'] = []
                    comp['alias_description'].append(comp.get('description', ''))
                    comp['alias_keys'].append(comp.get('keys', ''))
                    comp['alias_datasheet'].append(comp.get('datasheet',''))
                    last_alias=a

            # parse '$ADESC <TEXT>'
            match = re.match(r'\$ADESC\s+(.*)', line, re.IGNORECASE)
            if match:
                if len(last_alias) > 0: comp['alias_description'][-1] = match.group(1)

            # parse '$ADESCADD <TEXT>'
            match = re.match(r'\$ADESCADD\s+(.*)', line, re.IGNORECASE)
            if match:
                a=match.group(1)
                if len(a)>0:
                    if a[0].isalnum(): a=', '+a
                    if len(last_alias) > 0: comp['alias_description'][-1] = comp.get('description', '')+a

            # parse '$AKEYS <TEXT>'
            match = re.match(r'\$AKEYS\s+(.*)', line, re.IGNORECASE)
            if match:
                if len(last_alias) > 0: comp['alias_keys'][-1] = match.group(1)

            # parse '$AKEYSADD <TEXT>'
            match = re.match(r'\$AKEYSADD\s+(.*)', line, re.IGNORECASE)
            if match:
                a=match.group(1)
                if len(a)>0:
                    if a[0].isalnum(): a=' '+a
                    if len(last_alias) > 0: comp['alias_keys'][-1] = comp.get('keys', '')+a

            # parse '$ADATASHEET <TEXT>'
            match = re.match(r'\$ADATASHEET\s+(.*)', line, re.IGNORECASE)
            if match:
                if len(last_alias) > 0: comp['alias_datasheet'][-1] = match.group(1)

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


def implementComponent(lib, c, style_units):
    print('IMPLEMENTING', c['name'])
    print('   - aliases:', c['alias'])
    print('   - units:  ', c['units'])
    # remove old component
    lib.removeComponentOrAlias(c['name'])
    for a in c['alias']: lib.removeComponentOrAlias(a)
    print(len(c['units']))
    #comp=Component(style_units[c['name']].getComponentByName(c['name']))
    #comp.clearDRAW()
    
    


def main(libfilename, libdef_files, style):
    
    # read in style files
    print('READING STYLE ', style)
    style_units=readStyle(style)
    print(style_units)

    # parse library definition files in libdef_files
    
    component_templates=[]
    for libdef_fn in libdef_files:
        print('READING COMPONENT DEFINITION FILE ', libdef_fn)
        tl=readLIBDefinition(libdef_fn)
        print(tl)
        for t in tl:
            component_templates.append(t)

    #open library
    print ('OPENING LIBRARY FILE ', libfilename)
    lib = SchLib(libfilename)
    
    #implement components
    for c in component_templates:
        implementComponent(lib, c, style_units)

    # finally save the lib
    print('SAVING LIBRARY FILE ', libfilename)
    lib.save()
    










if __name__ == "__main__":
    # execute only if run as a script
    main("74xx.lib", [ os.path.join(os.getcwd(), 'symbol_generator_data', 'lib_def', 'logic_gates.txt')],  "ANSI")