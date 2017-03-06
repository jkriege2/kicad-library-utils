# -*- coding: utf-8 -*-

from __future__ import division


# math and comments from Michal script
# https://github.com/michal777/KiCad_Lib_Check

from rules.klc_constants import *
from rules.rule import *

class Rule(KLCRule):
    """
    Create the methods check and fix to use with the kicad_mod files.
    """
    def __init__(self, module, args):
        super(Rule, self).__init__(module, args, 'Rule 7.4', "Fabrication layer requirements")

    # Check for presence of component value
    def checkMissingValue(self):
        mod = self.module
        
        val = mod.value
        
        errors = []
        
        # Check for presense of 'value'
        if val['layer'] not in ['F.Fab', 'B.Fab']:
            errors.append("Component value is on layer {lyr} but should be on F.Fab or B.Fab".format(lyr=val['layer']))
        if val['hide']:
            errors.append("Component value is hidden (should be set to visible)")
        if val['font']['height'] != KLC_TEXT_SIZE:
            errors.append("Value label has a height of {1}mm (expected: {0}mm)".format(KLC_TEXT_SIZE, val['font']['height']))
        if val['font']['height'] != KLC_TEXT_SIZE:
            errors.append("Value label has a width of {1}mm (expected: {0}mm)".format(KLC_TEXT_SIZE, val['font']['width']))
        if val['font']['thickness'] != KLC_TEXT_THICKNESS:
            errors.append("Value label has a thickness of {1}mm (expected: {0}mm)".format(KLC_TEXT_THICKNESS, val['font']['thickness']))

        if len(errors) > 0:
            self.error("Value Label Errors")
            for err in errors:
                self.errorExtra(err)
            
        return len(errors) > 0
            
    def checkMissingLines(self):
        if len(self.f_fabrication_all) + len(self.b_fabrication_all) == 0:
            self.error("No drawings found on fabrication layer")
            return True
            
        return False
        
    def getSecondRef(self):
        texts = self.module.userText
        
        ref = None
        
        for text in texts:
            if text['user'] == '%R':
                ref = text
                break
                
        return ref
        
    # Check that there is a second ref '%R' on the fab layer
    def checkSecondRef(self):
        
        ref = self.getSecondRef()
        
        if not ref:
            self.error("Second Reference Designator missing")
            self.errorExtra("Add RefDes to F.Fab layer with '%R'")
            return True
            
        # Check that ref exists
        if ref['layer'] not in ['F.Fab', 'B.Fab']:
            self.error("Reference designator found on layer '{lyr}', expected '{exp}'".format(
                lyr = ref['layer'],
                exp = 'F.Fab'))
            return True
            
        # Check ref size
        font = ref['font']
        
        errors = []
        
        fh = font['height']
        fw = font['width']
        ft = font['thickness']
        
        # Font height 
        if not fh == fw:
            errors.append("RefDes aspect ratio should be 1:1")
            
        if fh < KLC_TEXT_SIZE_MIN or fh > KLC_TEXT_SIZE_MAX:
            errors.append("RefDes text size ({x}mm) is outside allowed range [{y}mm - {z}mm]".format(
                x = fh,
                y = KLC_TEXT_SIZE_MIN,
                z = KLC_TEXT_SIZE_MAX))
                
        # Font thickness
        if ft < KLC_TEXT_THICKNESS_MIN or ft > KLC_TEXT_THICKNESS_MAX:
            errors.append("RefDes text thickness ({x}mm) is outside allowed range [{y}mm - {z}mm]".format(
                x = ft,
                y = KLC_TEXT_SIZE_MIN,
                z = KLC_TEXT_SIZE_MAX))
            
        # Check position / orientation
        pos = ref['pos']
        
        if not pos['orientation'] == 0:
            errors.append("RefDes on F.Fab layer should be horizontal (no rotation)")
            
        if len(errors) > 0:
            self.error("RefDes errors")
            for err in errors:
                self.errorExtra(err)
            
        return len(errors) > 0
    
    # Check fab line widths
    def checkIncorrectWidth(self):
        self.bad_fabrication_width = []
        for graph in (self.f_fabrication_all + self.b_fabrication_all):
            if graph['width'] < KLC_FAB_WIDTH_MIN or graph['width'] > KLC_FAB_WIDTH_MAX:
                self.bad_fabrication_width.append(graph)
                
        msg = False
    
        if len(self.bad_fabrication_width) > 0:
            self.error("Some fabrication layer lines have a width outside allowed range of [{x}mm - {y}mm]".format(
                x = KLC_FAB_WIDTH_MIN,
                y = KLC_FAB_WIDTH_MAX))
                
            for g in self.bad_fabrication_width:
                self.errorExtra("{line}".format(line=g))
        
        return len(self.bad_fabrication_width) > 0
        
    def check(self):
        """
        Proceeds the checking of the rule.
        The following variables will be accessible after checking:
            * f_fabrication_all
            * b_fabrication_all
            * f_fabrication_lines
            * b_fabrication_lines
            * bad_fabrication_width
        """
        module = self.module
        self.f_fabrication_all = module.filterGraphs('F.Fab')
        self.b_fabrication_all = module.filterGraphs('B.Fab')

        self.f_fabrication_lines = module.filterLines('F.Fab')
        self.b_fabrication_lines = module.filterLines('B.Fab')
                
        return any([
                    self.checkMissingValue(),
                    self.checkMissingLines(),
                    self.checkIncorrectWidth(),
                    self.checkSecondRef(),
                    ])

    def fix(self):
        """
        Proceeds the fixing of the rule, if possible.
        """
        module = self.module
        if self.checkIncorrectWidth():
            for graph in self.bad_fabrication_width:
                graph['width'] = KLC_FAB_WIDTH
                
        if self.checkMissingValue():
            module.value['layer'] = 'F.Fab'
            module.value['font']['height'] = KLC_TEXT_SIZE
            module.value['font']['width'] = KLC_TEXT_SIZE
            module.value['font']['thickness'] = KLC_TEXT_THICKNESS
            
        if self.checkSecondRef():
            pass

