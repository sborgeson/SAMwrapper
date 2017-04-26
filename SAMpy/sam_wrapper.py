import os, sys
import numbers
import numpy as np
import pandas as pd
from SAMpy import PortablePySSC

class SAMEngine:

    def __init__(self, debug=False):
        self.debug = debug
        self.ssc  = PortablePySSC()

    @staticmethod
    def arr_to_str(a,maxN=10):
        if(len(a) > maxN):
            return '%s + %d more.' % ( str( a[ 0:(maxN) ] ), len(a) - maxN )
        else: return( str(a) )

    @staticmethod
    def mat_to_str(m, maxN=10):
        s = '' #','.join([''.join(['{:4}'.format(item) for item in row]) for row in m])
        return s

    def results_to_pandas(self, ssc_data, names):
        resultCols = {}
        for name in names:
            resultCols[name] = self.ssc.data_get_array(ssc_data, name)
        return pd.DataFrame(data=resultCols)

    def summarize(self, ssc_data):
        name = self.ssc.data_first(ssc_data)
        while (name != None):
            data_type = self.ssc.data_query(ssc_data, name)
            outstr = '\t'
            if data_type == self.ssc.STRING:
                outstr += ' str: ' + name + '    \'' + self.ssc.data_get_string(ssc_data, name) + '\''
            elif data_type == self.ssc.NUMBER:
                outstr += ' num: ' + name + '    ' + str(self.ssc.data_get_number(ssc_data, name))
            elif data_type == self.ssc.ARRAY:
                outstr += ' arr: ' + name + '    [ ' + self.arr_to_str(self.ssc.data_get_array(ssc_data, name), 2) + ' ]'
            elif data_type == self.ssc.MATRIX:
                outstr += ' mat: ' + name + '    [ ' + self.mat_to_str(self.ssc.data_get_matrix(ssc_data, name)) + ' ]'
            elif data_type == 5:
                outstr += ' tab: ' + name + '    TBD'
            else:
                outstr += ' inv! ' + name

            print(outstr)
            name = self.ssc.data_next(ssc_data)

    def set_from_dict(self, model_params, ssc_data):
        if self.debug: print('[set_from_dict] setting model_params')
        for key in model_params:
            value = model_params[key]
            if self.debug: print('%s : %s' % (key, type(value)) )
            # map numpy to standard types
            if isinstance(value, np.int64):   value = value.astype(int)
            if isinstance(value, np.float64): value = value.astype(float)
            if isinstance(value, np.ndarray): value = value.tolist()

            if isinstance(value, dict):
                subTable = self.ssc.data_create()                # create an empty SAM sub data table
                self.set_from_dict(value, subTable)              # insert values into sub table
                self.ssc.set_from_dict(ssc_data, key, subTable)  # set the sub table into the main table
            elif isinstance(value, numbers.Number):
                self.ssc.data_set_number(ssc_data, key, value)
            elif type(value) == str:
                self.ssc.data_set_string(ssc_data, key, value)
            elif type(value) == list and isinstance(value[0], numbers.Number):
                self.ssc.data_set_array(ssc_data, key, value)
            elif type(value) == list and isinstance(value[0], list):
                self.ssc.data_set_matrix(ssc_data, key, value)
            else:
                print('"%s" is not a type we know how ot map to SSC %s' % (key, type(ssc_data)))

    def clear_data(self,data): # clears all values from data object
        self.ssc.data_free(data)
  
    def unassign_data(self,data,varName): # celar a single variable from ssc data
        self.ssc.data_unassign(data, varName)

    def free_data(self,data):    # releases reference to entire data object
        self.ssc.data_free(data)

    def run_pvwatts(self, ssc_data=None, model_params=None, output_selector=None ):
        return( self.run_module( 'pvwattsv5', ssc_data=ssc_data, model_params=model_params, output_selector=output_selector ) )

    def run_pvsam(self, ssc_data=None, model_params=None, output_selector=None ):
        return( self.run_module( 'pvsamv1', ssc_data=ssc_data, model_params=model_params, output_selector=output_selector ) )

    def run_module(self, module_name, ssc_data=None, model_params=None, output_selector=None ):
        if ssc_data is None: ssc_data = self.ssc.data_create()

        if model_params is not None:
            if self.debug: print("Preparing SAM model data structure with model parameters")
            self.set_from_dict( model_params, ssc_data )
            if self.debug:
                print('data values set')
                self.summarize(ssc_data)

        if self.debug: print("Executing SAM Simulation using %s..." % (module_name))
        samModule = None
        try:
            samModule = self.ssc.module_create(module_name)
            if not self.debug: self.ssc.module_exec_set_print( 0 ) # no chatter during simulation
            runStatus = self.ssc.module_exec( samModule, ssc_data )
            if(runStatus != 1): raise Exception('Bad status from SAM simulation of %s.' % (module_name))
        finally:
            if samModule is not None: self.ssc.module_free(samModule)
        out = ssc_data
        if output_selector is not None:
            # TODO: this should be more sophisticated about what data it looks for and what type that data is
            # two use cases: return more than one variable of data at a time or return non-array data.
            # todo: include a look at "kwh_per_kw", which is present in both pvwatts and pvsam
            out = output_selector(ssc_data)  # self.ssc.data_get_array( sscData, outVar )
        return out



