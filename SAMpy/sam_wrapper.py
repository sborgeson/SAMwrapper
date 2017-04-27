# Copyright 2017, Sam Borgeson.
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
# Direct inquiries to Sam Borgeson (sam@convergenceda.com)

import os
import sys
import re
import numbers
import json
import numpy as np
import pandas as pd
from collections import OrderedDict
from SAMpy import PortablePySSC, weather_path, sam_path

class SAMEngine:

    def __init__(self, debug=False):
        self.debug = debug
        self.ssc  = PortablePySSC()

    @staticmethod
    def arr_to_str(a,maxN=10):
        if(len(a) > maxN):
            return '[ {} + {} more. ]'.format( ', '.join(str(x) for x in a[ 0:(maxN) ] ), len(a) - maxN )
        else: return( str(a) )

    @staticmethod
    def mat_to_str(m, maxRow=5, maxN=10):
        if (len(m) > maxRow):
            rowStrs = '\n'.join(SAMEngine.arr_to_str(row, maxN) for row in m[0:maxRow])
            #s = '' #','.join([''.join(['{:4}'.format(item) for item in row]) for row in m])
            return '[ {}\n ... \n and {} more\n ]'.format(rowStrs, len(m)-maxRow)
        else:
            return (str(m))

    def results_to_pandas(self, ssc_data, names, ):
        resultCols = {}
        for name in names:
            resultCols[name] = self.ssc.data_get_array(ssc_data, name)
        dt_hrs = pd.date_range('1/1/2015', periods=8760, freq='H')
        return pd.DataFrame(data=resultCols, index=dt_hrs)

    def summarize(self, ssc_data):
        name = self.ssc.data_first(ssc_data) # note that this is bytes, which must be converted to a str in python 3
        outstr = ''
        while (name != None):
            nameStr = str(name)
            data_type = self.ssc.data_query(ssc_data, name)
            outstr += '\t'
            if data_type == self.ssc.STRING:
                outstr += " str: {}\t'{}'".format(nameStr, str(self.ssc.data_get_string(ssc_data, name)))
            elif data_type == self.ssc.NUMBER:
                outstr += ' num: {}\t{}'.format(nameStr, str(self.ssc.data_get_number(ssc_data, name)))
            elif data_type == self.ssc.ARRAY:
                outstr += ' arr: {}\t{}'.format(nameStr, self.arr_to_str(self.ssc.data_get_array(ssc_data, name), 2))
            elif data_type == self.ssc.MATRIX:
                outstr += ' mat: {}\t{}'.format(nameStr, self.mat_to_str(self.ssc.data_get_matrix(ssc_data, name),2,2))
            elif data_type == 5:
                outstr += ' tab: {}\t{}'.format(name, 'TBD')
            else:
                outstr += ' inv! {}'.format(name)
            outstr += '\n'
            name = self.ssc.data_next(ssc_data) # bytes converted to str
        return outstr

    def set_from_dict(self, model_params, ssc_data):
        if self.debug: print('[set_from_dict] setting model_params')
        for key in model_params:
            value = model_params[key]
            if self.debug: print('  {} {} : {}'.format(type(value).__name__, key, value) )
            # map numpy to standard types
            if isinstance(value, np.int64):   value = value.astype(int)
            if isinstance(value, np.float64): value = value.astype(float)
            if isinstance(value, np.ndarray): value = value.tolist()

            # implement the default weather data path fallback mechanism
            if key == 'solar_resource_file':
                if not os.path.isfile(value):
                    if weather_path != '':
                        value = os.path.join(weather_path, value)
                    else:
                        value = os.path.join(sam_path, 'solar_resource', value)
                    if self.debug: print('  Modified solar_resource_file: {}'.format(value))
            # if the value is a dict, create a new SAM data object and populate it with the dict values
            if isinstance(value, dict):
                subTable = self.ssc.data_create()                # create an empty SAM sub data table
                self.set_from_dict(value, subTable)              # insert values into sub table
                self.ssc.set_from_dict(ssc_data, key, subTable)  # set the sub table into the main table
            elif isinstance(value, numbers.Number):
                self.ssc.data_set_number(ssc_data, key, value)
            elif type(value) == str or type(value) == unicode:
                self.ssc.data_set_string(ssc_data, key, value)
            elif type(value) == list and isinstance(value[0], numbers.Number):
                self.ssc.data_set_array(ssc_data, key, value)
            elif type(value) == list and isinstance(value[0], list):
                self.ssc.data_set_matrix(ssc_data, key, value)
            else:
                print('"{}" is not a type we know how to map to SSC {}'.format(key, type(ssc_data)))

    def clear_data(self,data): # clears all values from data object
        self.ssc.data_free(data)
  
    def unassign_data(self,data,varName): # celar a single variable from ssc data
        self.ssc.data_unassign(data, varName)

    def free_data(self,data):    # releases reference to entire data object
        self.ssc.data_free(data)

    def run_pvwatts(self, ssc_data=None, model_params=None, lk_script=None, output_selector=None ):
        return( self.run_module( 'pvwattsv5', ssc_data=ssc_data, model_params=model_params, lk_script=lk_script, output_selector=output_selector ) )

    def run_pvsam(self, ssc_data=None, model_params=None, lk_script=None, output_selector=None ):
        return( self.run_module( 'pvsamv1', ssc_data=ssc_data, model_params=model_params, lk_script=lk_script, output_selector=output_selector ) )

    def run_module(self, module_name, ssc_data=None, model_params=None, lk_script=None, output_selector=None ):
        if ssc_data is None: ssc_data = self.ssc.data_create()
        ssc_config = {}
        if lk_script is not None:
            if self.debug: print("[run_module] Using parameters from lk as base input")
            lk_params = LKInterpreter(lk_script).sam_vars_to_dict()
            ssc_config.update(lk_params)
        if model_params is not None:
            if self.debug: print("[run_module] Using passed model parameters as model inputs")
            ssc_config.update(model_params)
        if self.debug: print("[run_module] Preparing SAM model data structure with model parameters")
        self.set_from_dict( ssc_config, ssc_data )
        if self.debug:
            print('[rum_module] Data values set. Here they are:')
            print(self.summarize(ssc_data))
            print()

        samModule = None
        try:
            samModule = self.ssc.module_create(module_name)
            if self.debug: print("[run_module] Executing SAM Simulation using {}...".format(module_name))
            if not self.debug: self.ssc.module_exec_set_print( 0 ) # no chatter during simulation
            runStatus = self.ssc.module_exec( samModule, ssc_data )
            if(runStatus != 1): raise Exception('Bad status from SAM simulation of {}.'.format(module_name))
        finally:
            if samModule is not None: self.ssc.module_free(samModule)
        out = ssc_data
        if output_selector is not None:
            # TODO: this should be more sophisticated about what data it looks for and what type that data is
            # two use cases: return more than one variable of data at a time or return non-array data.
            # todo: include a look at "kwh_per_kw", which is present in both pvwatts and pvsam
            out = output_selector(ssc_data)  # self.ssc.data_get_array( sscData, outVar )
        return out


class LKInterpreter():
    '''You can press Shift F5 to generate an LK script file that sets the values of the input
    variables for each SSC module your SAM cases uses to the SAM input values. This class can
    interpret those files.
    Note: this class only looks for var setting commands and doesn't do anything else that LK does.'''
    # match variable name, value in the form "var('variable name', value );"
    # the DOTALL allows matches to span newlines and the (.+?) groups are non-greedy matches
    varRE = re.compile('var\s*\(\s*\'(.+?)\'\s*\,\s*(.+?)\s*\)\;', re.DOTALL)
    text1RE = re.compile('\s*\'(.*)\'\s*')  # single quotes
    text2RE = re.compile('\s*\"(.*)\"\s*')  # double quotes

    def __init__(self, fpath):
        with open(fpath, 'r') as lkFile:
            self.lkText = lkFile.read()

    def sam_vars_to_dict(self):
        samVars = OrderedDict()
        for i, match in enumerate(self.varRE.finditer(self.lkText)):
            (var, val) = (match.group(1), match.group(2))
            # look for quote enclosed text
            t1 = self.text1RE.search(val)
            t2 = self.text2RE.search(val)
            if t1 is not None:
                val = t1.group(1)
            elif t2 is not None:
                val = t2.group(1)
            # fall back to json parsing of numbers and more complex data
            # Note this *seems* to cover all cases
            else:
                try:
                    val = json.loads(val)
                except ValueError:
                    print("JSON can't parse %s, %s" % (var, val))
            samVars[var] = val
        return (samVars)

