# coding: utf-8
"""
pygaarst.irutils

Utility functions for calculations on infrared data. Refactored from 
pygaarst.landsatutils

Created by Chris Waigl on 2014-04-30.
"""

from __future__ import division

import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.irutils')

# Constants
KtoC = 273.15

# Helpers
class _FPErr_Log(object):
    def __init__(self, custmsg):
        self.custmsg = custmsg
    def write(self, errmsg):
        LOGGER.warning("%s: %s" % (self.custmsg, errmsg))

# Functions
def gainbias(lmax, lmin, qcalmax, qcalmin):
    gain = (lmax - lmin)/(qcalmax - qcalmin)
    bias = (qcalmax*lmin - qcalmin*lmax)/(qcalmax - qcalmin)
    return gain, bias

def dn2rad(data, gain, bias):
    return data * gain + bias

def rad2kelvin(data, k1, k2):
    return np.divide(k2, np.log(np.divide(k1, data) + 1))

def rad2celsius(data, k1, k2, ktoc=KtoC):
    return rad2kelvin(data, k1, k2) - ktoc

def normdiff(array1, array2):
    log = _FPErr_Log("NaN generated while calculating normalized difference index: ")
    np.seterrcall(log)
    np.seterr(invalid='log')
    nd = np.divide(
            array1.astype(np.float32) - array2.astype(np.float32), 
            array1.astype(np.float32) + array2.astype(np.float32)
            )
    return nd

