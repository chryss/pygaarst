# coding: utf-8
"""
pygaarst.irutils

Utility functions for calculations on infrared data. Refactored from
pygaarst.landsatutils

Created by Chris Waigl on 2014-04-30.
"""

from __future__ import division, print_function, absolute_import

import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.irutils')

# Constants; SI units except for lambda
KtoC = 273.15
h = 6.626068e-34  # Planck's constant, m^2 kg / s
c = 2.99792e8 # speed of light, m / s
kB = 1.38065e-23 # Boltzmann's constant, m^2 kg / s^2 / K

# Helpers
class _FPErr_Log(object):
    """Special class to catch arithmetic errors"""
    def __init__(self, custmsg):
        self.custmsg = custmsg
    def write(self, errmsg):
        """Writes log message"""
        LOGGER.warning("%s: %s" % (self.custmsg, errmsg))

# Functions
def gainbias(lmax, lmin, qcalmax, qcalmin):
    """Calculates gain and bias from max and min radiance"""
    gain = (lmax - lmin)/(qcalmax - qcalmin)
    bias = (qcalmax*lmin - qcalmin*lmax)/(qcalmax - qcalmin)
    return gain, bias

def dn2rad(data, gain, bias):
    """Converts digital number array to radiance"""
    return data * gain + bias

def rad2kelvin(data, k1, k2):
    """Converts radiance array to temperature in Kelvin"""
    return np.divide(k2, np.log(np.divide(k1, data) + 1))

def rad2celsius(data, k1, k2, ktoc=KtoC):
    """Converts radiance array to temperature in Celsius"""
    return rad2kelvin(data, k1, k2) - ktoc

def normdiff(array1, array2):
    """Calculates normalized difference index array from input arrays"""
    log = _FPErr_Log(
        "NaN generated while calculating normalized difference index: ")
    np.seterrcall(log)
    np.seterr(invalid='log')
    normalizeddiff = np.divide(
        array1.astype(np.float32) - array2.astype(np.float32),
        array1.astype(np.float32) + array2.astype(np.float32))
    return normalizeddiff

def specrad(lamb, T):
    """
    Calculates blackbody spectral radiance at temperature T

    Spectral radiance in W/m^2/um/sr; T in K; lambda in micrometres
    """
    lamb = lamb * 1.0e-6 # convert from micrometres to metres
    rad = 1.0e-6 * (2*h*c**2) / (lamb**5*(np.exp((h*c)/(lamb*kB*T)) - 1))
    return rad

