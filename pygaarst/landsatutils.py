# coding: utf-8
"""
pygaarst.landsatutils

Utility functions for parsing Landsat metadata files

Created by Chris Waigl on 2013-11-13.
Implemented:
  - Landsat
"""

from __future__ import division

import os.path, glob
import datetime
import re
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.raster')

# ================================
# = Landsat parameters for bands =
# ================================

LANDSATBANDS = {
    'L4': ['1', '2', '3', '4', '5', '6', '7'],
    'L5': ['1', '2', '3', '4', '5', '6', '7'],
    'L7': ['1', '2', '3', '4', '5', '6L', '6H', '7'],
    'L8': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
}

def get_bands(spacecraftid):
    try:
        return LANDSATBANDS[spacecraftid]
    except KeyError:
        logging.error("Band labels are available for TM, ETM+ and OLI/TIR sensors on %s." % ', '.join(LANDSATBANDS.keys()))

# ==================================================================
# = Landsat metadata parsing                                       =
#
# The metadata file looks like this:
# GROUP = L1_METADATA_FILE
#   GROUP = METADATA_FILE_INFO
#     ORIGIN = "Image courtesy of the U.S. Geological Survey"
#     REQUEST_ID = "0501306252996_00005"
#     ...
#     STATION_ID = "LGN"
#     PROCESSING_SOFTWARE_VERSION = "LPGS_2.2.2"
#  END_GROUP = METADATA_FILE_INFO
#  GROUP = PRODUCT_METADATA
#     DATA_TYPE = "L1T"
#     ...
#  END_GROUP = PRODUCT_METADATA
#  END_GROUP = L1_METADATA_FILE
#  END
# ==================================================================

# Landsat metadata files end in _MTL.txt or _MTL.TXT
METAPATTERN = "*_MTL*"

# Elements from the file format used for parsing
GRPSTART = "GROUP = "
GRPEND = "END_GROUP = "
ASSIGNCHAR = " = "
FINAL = "END"

# A simple state machine is used to parse the file. There are 5 states (0 to 4):
STATUSCODE = [
    "begin",
    "enter metadata group",
    "add metadata item",
    "leave metadata group",
    "end"
    ]

# A custom exception for this module
class LandsatMTLParseError(Exception):
    pass

# Help functions to identify the current line and extract information
def _islinetype(line, testchar):
    return line.strip().startswith(testchar)

def _isassignment(line):
    return ASSIGNCHAR in line

def _isfinal(line):
    return line.strip() == FINAL

def _getgroupname(line):
    return line.strip().split(GRPSTART)[-1]

def _getendgroupname(line):
    return line.strip().split(GRPEND)[-1]

def _getmetadataitem(line):
    return line.strip().split(ASSIGNCHAR)

# After reading a line, what state we're in depends on the line and the state before reading
def _checkstatus(status, line):
    """returns state/status after reading the next line"""
    newstatus = 0
    if status == 0:
        # begin --> enter metadata group OR end
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _isfinal(line):
            newstatus = 4
    elif status == 1:
        # enter metadata group --> enter metadata group OR add metadata item OR leave metadata group
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, GRPEND):
            newstatus = 3
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    elif status == 2:
        if _islinetype(line, GRPEND):
            newstatus = 3
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    elif status == 3:
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, GRPEND):
            newstatus = 3
        elif _isfinal(line):
            newstatus = 4
    if newstatus != 0:
        return newstatus
    elif status != 4:
        raise LandsatMTLParseError("Cannot parse the following line after status '%s':\n%s" % (STATUSCODE[status], line))

# Function to execute when reading a line in a given state
def _transstat(status, grouppath, dictpath, line):
    if status == 0:
        raise LandsatMTLParseError("Status should not be '%s' after reading line:\n%s" % (STATUSCODE[status], line))
    elif status == 1:
        currentdict = dictpath[-1]
        currentgroup = _getgroupname(line)
        grouppath.append(currentgroup)
        currentdict[currentgroup] = {}
        dictpath.append(currentdict[currentgroup])
    elif status == 2:
        currentdict = dictpath[-1]
        newkey, newval = _getmetadataitem(line)
        currentdict[newkey] = _postprocess(newval)
    elif status == 3:
        oldgroup = _getendgroupname(line)
        if oldgroup != grouppath[-1]:
            raise LandsatMTLParseError("Reached line '%s' while reading group '%s'." % (line.strip(), grouppath[-1]))
        del grouppath[-1]
        del dictpath[-1]
        try:
            currentgroup = grouppath[-1]
        except IndexError:
            currentgroup = None
    elif status == 4:
        if grouppath:
            raise LandsatMTLParseError("Reached end before end of group '%s'" % grouppath[-1])
    return grouppath, dictpath

# Identifying data type of a metadata item and
def _postprocess(valuestr):
    """Takes value as string, returns string, integer, float, date, datetime, or time"""
    intpattern = re.compile(r'^\-?\d+$')
    floatpattern = re.compile(r'^\-?\d+\.\d+(E[+-]?\d\d+)?$')
    datedtpattern = '%Y-%m-%d'
    datedttimepattern = '%Y-%m-%dT%H:%M:%SZ'
    timedtpattern = '%H:%M:%S.%f'
    timepattern = re.compile(r'^\d{2}:\d{2}:\d{2}(\.\d{6})?')
    if valuestr.startswith('"') and valuestr.endswith('"'):
        # it's a string
        return valuestr[1:-1]
    elif re.match(intpattern, valuestr):
        # it's an integer
        return int(valuestr)
    elif re.match(floatpattern, valuestr):
        # floating point number
        return float(valuestr)
    # now let's try the datetime objects ; throws exception if it doesn't match
    try:
        return datetime.datetime.strptime(valuestr, datedtpattern).date()
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(valuestr, datedttimepattern)
    except ValueError:
        pass
    # time parsing is complicated: Python's datetime module only accepts
    # fractions of a second only up to 6 digits
    mat = re.match(timepattern, valuestr)
    if mat:
        test = mat.group(0)
        try:
            return datetime.datetime.strptime(test, timedtpattern).time()
        except ValueError:
            pass

    # If we get here, we still haven't returned anything.
    logging.info("The value %s couldn't be parsed as int, float, date, time, datetime. Returning it as string." % valuestr)
    return valuestr

def parsemeta(metadataloc):
    """metadataloc: a filename or a directory. Returns metadata dictionary"""

    # filename or directory? if several fit, use first one and warn
    if os.path.isdir(metadataloc):
        metalist = glob.glob(os.path.join(metadataloc, METAPATTERN))
        if not metalist:
            raise LandsatMTLParseError("No files matching metadata file pattern in directory %s." % metadataloc)
        elif len(metalist) > 0:
            metadatafn = metalist[0]
            if len(metalist) > 1:
                logging.warning("More than one file in directory match metadata file pattern. Using %s." % metadatafn)
    elif os.path.isfile(metadataloc):
        metadatafn = metadataloc
        logging.info("Using file %s." % metadatafn)
    else:
        raise LandsatMTLParseError("File location %s is unavailable or doesn't contain a suitable metadata file." % metadataloc)

    # Reading file line by line and inserting data into metadata dictionary
    status = 0
    metadata = {}
    grouppath = []
    dictpath = [metadata]
    with open(metadatafn, 'rU') as fn:
        for line in fn:
            if status == 4:
                # we reached the end in the previous iteration, but are still reading lines
                logging.warning("Found end before finishing file parsing.")
            status = _checkstatus(status, line)
            grouppath, dictpath = _transstat(status, grouppath, dictpath, line)
    return metadata

def lskeyselect(isnew, keystr):
    """
    Translates key strings from old to new metadata format, dependent on self.newmetaformat
    (Boolean). See http://landsat.usgs.gov/Landsat_Metadata_Changes.php for changes in August 2012.\
        Only implemented for keys that are used in this module.
    """
    new2old = {
        'DATE_ACQUIRED': 'ACQUISITION_DATE'
    }
    if not isnew:
        try:
            return new2old[keystr]
        except KeyError:
            logging.warning("Key %s might not be valid for old-style metadata files." % keystr)
    else:
        return keystr



# =====================================================================
# = Landat Thermal Bands Radiance to Brightness Temperature Conversion =
#
# See Chander, G., Markham, B. L., Helder, D.L. (2009):
# Summary of current radiometric calibration coefficients for Landsat
# MSS, TM, ETM+, and EO-1 ALI sensors, Remote Sensing of Environment, 893-903.
# http://dx.doi.org/10.1016/j.rse.2009.01.007
#
# K1 in W/(m^s sr μm). K2 in K
# See also http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
# =====================================================================

# Constants for Landsat 4, 5, 7
# NOTE: For Landat 8/LCM the K1 and K2 constants are provided in the metadata

K1_L4_TM = 671.62
K2_L4_TM = 1284.30
K1_L5_TM = 607.76
K2_L5_TM = 1260.56
K1_L7_EMTplus = 666.09
K2_L7_EMTplus = 1282.71
KtoC = 273.15

def getKconstants(spacecraftid):
    if spacecraftid == 'L4':
        return K1_L4_TM, K2_L4_TM
    elif spacecraftid == 'L5':
        return K1_L5_TM, K2_L5_TM
    elif spacecraftid == 'L7':
        return K1_L7_EMTplus, K2_L7_EMTplus
    else:
        logging.warning('SpacecraftID not in L4, L5, L7. Check metadata or spacecraftID. Or both.')

def gainbias(lmax, lmin, qcalmax, qcalmin):
    gain = (lmax - lmin)/(qcalmax - qcalmin)
    bias = (qcalmax*lmin - qcalmin*lmax)/(qcalmax - qcalmin)
    return gain, bias

def dn2rad(data, gain, bias):
    return data * gain + bias

def rad2kelvin(data, k1, k2):
    return np.divide(k2, np.log(np.divide(k1, data) + 1))

def rad2celsius(data, k1, k2):
    return rad2kelvin(data, k1, k2) - KtoC

# =============================
# = Landsat DN to reflectance =
# =============================
# Currently only L5, L7, L8


# Earth-sun distance, see http://landsathandbook.gsfc.nasa.gov/data_prod/prog_sect11_3.html
# as a function of julian day

DISTEARTHSUN = {
    1: 0.98331,
    2: 0.98330,
    3: 0.98330,
    4: 0.98330,
    5: 0.98330,
    6: 0.98332,
    7: 0.98333,
    8: 0.98335,
    9: 0.98338,
    10: 0.98341,
    11: 0.98345,
    12: 0.98349,
    13: 0.98354,
    14: 0.98359,
    15: 0.98365,
    16: 0.98371,
    17: 0.98378,
    18: 0.98385,
    19: 0.98393,
    20: 0.98401,
    21: 0.98410,
    22: 0.98419,
    23: 0.98428,
    24: 0.98439,
    25: 0.98449,
    26: 0.98460,
    27: 0.98472,
    28: 0.98484,
    29: 0.98496,
    30: 0.98509,
    31: 0.98523,
    32: 0.98536,
    33: 0.98551,
    34: 0.98565,
    35: 0.98580,
    36: 0.98596,
    37: 0.98612,
    38: 0.98628,
    39: 0.98645,
    40: 0.98662,
    41: 0.98680,
    42: 0.98698,
    43: 0.98717,
    44: 0.98735,
    45: 0.98755,
    46: 0.98774,
    47: 0.98794,
    48: 0.98814,
    49: 0.98835,
    50: 0.98856,
    51: 0.98877,
    52: 0.98899,
    53: 0.98921,
    54: 0.98944,
    55: 0.98966,
    56: 0.98989,
    57: 0.99012,
    58: 0.99036,
    59: 0.99060,
    60: 0.99084,
    61: 0.99108,
    62: 0.99133,
    63: 0.99158,
    64: 0.99183,
    65: 0.99208,
    66: 0.99234,
    67: 0.99260,
    68: 0.99286,
    69: 0.99312,
    70: 0.99339,
    71: 0.99365,
    72: 0.99392,
    73: 0.99419,
    74: 0.99446,
    75: 0.99474,
    76: 0.99501,
    77: 0.99529,
    78: 0.99556,
    79: 0.99584,
    80: 0.99612,
    81: 0.99640,
    82: 0.99669,
    83: 0.99697,
    84: 0.99725,
    85: 0.99754,
    86: 0.99782,
    87: 0.99811,
    88: 0.99840,
    89: 0.99868,
    90: 0.99897,
    91: 0.99926,
    92: 0.99954,
    93: 0.99983,
    94: 1.00012,
    95: 1.00041,
    96: 1.00069,
    97: 1.00098,
    98: 1.00127,
    99: 1.00155,
    100: 1.00184,
    101: 1.00212,
    102: 1.00240,
    103: 1.00269,
    104: 1.00297,
    105: 1.00325,
    106: 1.00353,
    107: 1.00381,
    108: 1.00409,
    109: 1.00437,
    110: 1.00464,
    111: 1.00492,
    112: 1.00519,
    113: 1.00546,
    114: 1.00573,
    115: 1.00600,
    116: 1.00626,
    117: 1.00653,
    118: 1.00679,
    119: 1.00705,
    120: 1.00731,
    121: 1.00756,
    122: 1.00781,
    123: 1.00806,
    124: 1.00831,
    125: 1.00856,
    126: 1.00880,
    127: 1.00904,
    128: 1.00928,
    129: 1.00952,
    130: 1.00975,
    131: 1.00998,
    132: 1.01020,
    133: 1.01043,
    134: 1.01065,
    135: 1.01087,
    136: 1.01108,
    137: 1.01129,
    138: 1.01150,
    139: 1.01170,
    140: 1.01191,
    141: 1.01210,
    142: 1.01230,
    143: 1.01249,
    144: 1.01267,
    145: 1.01286,
    146: 1.01304,
    147: 1.01321,
    148: 1.01338,
    149: 1.01355,
    150: 1.01371,
    151: 1.01387,
    152: 1.01403,
    153: 1.01418,
    154: 1.01433,
    155: 1.01447,
    156: 1.01461,
    157: 1.01475,
    158: 1.01488,
    159: 1.01500,
    160: 1.01513,
    161: 1.01524,
    162: 1.01536,
    163: 1.01547,
    164: 1.01557,
    165: 1.01567,
    166: 1.01577,
    167: 1.01586,
    168: 1.01595,
    169: 1.01603,
    170: 1.01610,
    171: 1.01618,
    172: 1.01625,
    173: 1.01631,
    174: 1.01637,
    175: 1.01642,
    176: 1.01647,
    177: 1.01652,
    178: 1.01656,
    179: 1.01659,
    180: 1.01662,
    181: 1.01665,
    182: 1.01667,
    183: 1.01668,
    184: 1.01670,
    185: 1.01670,
    186: 1.01670,
    187: 1.01670,
    188: 1.01669,
    189: 1.01668,
    190: 1.01666,
    191: 1.01664,
    192: 1.01661,
    193: 1.01658,
    194: 1.01655,
    195: 1.01650,
    196: 1.01646,
    197: 1.01641,
    198: 1.01635,
    199: 1.01629,
    200: 1.01623,
    201: 1.01616,
    202: 1.01609,
    203: 1.01601,
    204: 1.01592,
    205: 1.01584,
    206: 1.01575,
    207: 1.01565,
    208: 1.01555,
    209: 1.01544,
    210: 1.01533,
    211: 1.01522,
    212: 1.01510,
    213: 1.01497,
    214: 1.01485,
    215: 1.01471,
    216: 1.01458,
    217: 1.01444,
    218: 1.01429,
    219: 1.01414,
    220: 1.01399,
    221: 1.01383,
    222: 1.01367,
    223: 1.01351,
    224: 1.01334,
    225: 1.01317,
    226: 1.01299,
    227: 1.01281,
    228: 1.01263,
    229: 1.01244,
    230: 1.01225,
    231: 1.01205,
    232: 1.01186,
    233: 1.01165,
    234: 1.01145,
    235: 1.01124,
    236: 1.01103,
    237: 1.01081,
    238: 1.01060,
    239: 1.01037,
    240: 1.01015,
    241: 1.00992,
    242: 1.00969,
    243: 1.00946,
    244: 1.00922,
    245: 1.00898,
    246: 1.00874,
    247: 1.00850,
    248: 1.00825,
    249: 1.00800,
    250: 1.00775,
    251: 1.00750,
    252: 1.00724,
    253: 1.00698,
    254: 1.00672,
    255: 1.00646,
    256: 1.00620,
    257: 1.00593,
    258: 1.00566,
    259: 1.00539,
    260: 1.00512,
    261: 1.00485,
    262: 1.00457,
    263: 1.00430,
    264: 1.00402,
    265: 1.00374,
    266: 1.00346,
    267: 1.00318,
    268: 1.00290,
    269: 1.00262,
    270: 1.00234,
    271: 1.00205,
    272: 1.00177,
    273: 1.00148,
    274: 1.00119,
    275: 1.00091,
    276: 1.00062,
    277: 1.00033,
    278: 1.00005,
    279: 0.99976,
    280: 0.99947,
    281: 0.99918,
    282: 0.99890,
    283: 0.99861,
    284: 0.99832,
    285: 0.99804,
    286: 0.99775,
    287: 0.99747,
    288: 0.99718,
    289: 0.99690,
    290: 0.99662,
    291: 0.99634,
    292: 0.99605,
    293: 0.99577,
    294: 0.99550,
    295: 0.99522,
    296: 0.99494,
    297: 0.99467,
    298: 0.99440,
    299: 0.99412,
    300: 0.99385,
    301: 0.99359,
    302: 0.99332,
    303: 0.99306,
    304: 0.99279,
    305: 0.99253,
    306: 0.99228,
    307: 0.99202,
    308: 0.99177,
    309: 0.99152,
    310: 0.99127,
    311: 0.99102,
    312: 0.99078,
    313: 0.99054,
    314: 0.99030,
    315: 0.99007,
    316: 0.98983,
    317: 0.98961,
    318: 0.98938,
    319: 0.98916,
    320: 0.98894,
    321: 0.98872,
    322: 0.98851,
    323: 0.98830,
    324: 0.98809,
    325: 0.98789,
    326: 0.98769,
    327: 0.98750,
    328: 0.98731,
    329: 0.98712,
    330: 0.98694,
    331: 0.98676,
    332: 0.98658,
    333: 0.98641,
    334: 0.98624,
    335: 0.98608,
    336: 0.98592,
    337: 0.98577,
    338: 0.98562,
    339: 0.98547,
    340: 0.98533,
    341: 0.98519,
    342: 0.98506,
    343: 0.98493,
    344: 0.98481,
    345: 0.98469,
    346: 0.98457,
    347: 0.98446,
    348: 0.98436,
    349: 0.98426,
    350: 0.98416,
    351: 0.98407,
    352: 0.98399,
    353: 0.98391,
    354: 0.98383,
    355: 0.98376,
    356: 0.98370,
    357: 0.98363,
    358: 0.98358,
    359: 0.98353,
    360: 0.98348,
    361: 0.98344,
    362: 0.98340,
    363: 0.98337,
    364: 0.98335,
    365: 0.98333,
    366: 0.98331
    }

ESUN = {
    'L7': {
        '1': 1970.,
        '2': 1842.,
        '3': 1547.,
        '4': 1044.,
        '5': 225.7,
        '7': 82.06,
        '8': 1369.
    },
    'L5': {
        '1': 1997.,
        '2': 1812.,
        '3': 1533.,
        '4': 1039.,
        '5': 225.7,
        '7': 84.9,
        '8': 1362.
    }
}

def getd(julianday):
    return DISTEARTHSUN[julianday]

def getesun(spacecraft, band):
    return ESUN[spacecraft][band]

# =========================================
# = Landsat vegetation indices parameters =
# =========================================

NDVI_BANDS = {
    'L4': ('band4', 'band3'),
    'L5': ('band4', 'band3'),
    'L7': ('band4', 'band3'),
    'L8': ('band5', 'band4')
    }

NBR_BANDS = {
    'L4': ('band4', 'band7'),
    'L5': ('band4', 'band7'),
    'L7': ('band4', 'band7'),
    'L8': ('band5', 'band7'),
    }

def normdiff(array1, array2):
    return np.divide(
        array1.astype(np.float32) - array2.astype(np.float32), 
        array1.astype(np.float32) + array2.astype(np.float32)
        )

# ========================================
# = Cloud masking algorithms for Landsat =
# ========================================

def naivethermal(tirband, tb=280.):
    """Takes LandsatBand object, must be TIR to make sense. Returns numpy array"""
    out = np.zeros(tirband.data.shape)
    out[tirband.tKelvin < tb] = 1.
    return out
    
    
def LTKcloud(lsscene):
    """Luo–Trishchenko–Khlopenkov"""
    if lsscene.spacecraft == 'L8':
        d1, d3, d4, d5 = lsscene.band2.reflectance, lsscene.band4.reflectance, lsscene.band5.reflectance, lsscene.band6.reflectance
    else:
        d1, d3, d4, d5 = lsscene.band1.reflectance, lsscene.band3.reflectance, lsscene.band4.reflectance, lsscene.band5.reflectance
    
    # calculate masks
    dummy1 = np.logical_and(d1<d3, np.logical_and(d3<d4, np.logical_and(d4<d5*1.07, d5 < 0.65)))
    dummy2 = np.logical_and(d1*0.8<d3, np.logical_and(d3<d4*0.8, np.logical_and(d4<d5, d3<0.22)))
    mask_bareland = np.logical_or(dummy1, dummy2)
    dummy3 = np.logical_and(d3>0.24, np.logical_and(d5<0.16, d3>d4))
    dummy4 = np.logical_and(0.24>d3, np.logical_and(d3>0.18, np.logical_and(d5<d3-0.08, d3>d4)))
    mask_ice = np.logical_or(dummy3, dummy4)
    dummy5 = np.logical_and(d3>d4, np.logical_and(d3>d5*0.67, np.logical_and(d1<0.3, d3<0.2)))
    dummy6 = np.logical_and(d3>d4*0.8, np.logical_and(d3>d5*0.67, d3<0.06))
    mask_water = np.logical_or(dummy5, dummy6)
    dummy7 = np.logical_or(d1>0.2, d3>0.18)
    mask_cloud = np.logical_and(dummy7, np.logical_and(d5 > 0.16, np.maximum(d1, d3) > d5*0.67))
    
    # apply masks to array
    out = np.zeros(d1.shape)
    out[mask_bareland] = 1.
    nextmask = np.logical_and(~mask_bareland, mask_ice)
    out[nextmask] = 2.
    union = np.logical_or(mask_bareland, mask_ice)
    nextmask = np.logical_and(~union, mask_water)
    out[nextmask] = 3.
    union = np.logical_or(union, mask_water)
    nextmask = np.logical_and(~union, mask_cloud)
    out[nextmask] = 4.
    union = np.logical_or(union, mask_cloud)
    out[~union] = 5.
    
    return out