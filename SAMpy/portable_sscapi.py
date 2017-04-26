import os, sys
import json
import struct
from ctypes import CDLL
from SAMpy import get_sdk_path, PySSC

class PortablePySSC(PySSC):
    '''An extension of the standard PySSC class (which hard codes share library paths to one
    that points to a configurable location'''

    def __init__(self, sdk_path=None):
        # SAM sdk path. For example: 'C:/SAM/2017.1.17/sam-sdk-2017-1-17-r1'
        if sdk_path is None:
            sdk_path = get_sdk_path()
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            if 8*struct.calcsize("P") == 64:
                print (os.path.join(sdk_path, 'win64','ssc.dll'))
                self.pdll = CDLL(os.path.join(sdk_path, 'win64', 'ssc.dll'))
            else:
                self.pdll = CDLL(os.path.join(sdk_path, 'win32', 'ssc.dll'))
        elif sys.platform == 'darwin':
            self.pdll = CDLL(os.path.join(sdk_path, "osx64', 'ssc.dylib"))
        elif sys.platform == 'linux2':
            self.pdll = CDLL(os.path.join(sdk_path, "linux64', 'ssc.so"))
        else:
            print("Platform not supported ", sys.platform)

