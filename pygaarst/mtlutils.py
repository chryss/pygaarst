# coding: utf-8
"""
pygaarst.mtlutils

Helpers for parsing MTL metadata files used by USGS Landsat and EO-1
(Hyperion and ALI) Level 1 GeoTIFF scene data archives

Created by Chris Waigl on 2014-04-20.

[2014-04-20] Refactoring original landsatutils.py, as MTL file format is
also used by Hyperion and ALI.
"""

from __future__ import division, print_function, absolute_import

import os.path, glob
import datetime
import re
from StringIO import StringIO
from ast import literal_eval
from collections import OrderedDict
import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.mtlutils')

# ==================================================================
# = USGS MTL metadata parsing for Landsat, ALI, Hyperion
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
GRPSTART = "GROUP="
GRPEND = "END_GROUP="
OBJSTART = "OBJECT="
OBJEND = "END_OBJECT="
ASSIGNCHAR = "="
FINAL = "END"
IGNOREGROUPS = [
    "INFORMATIONCONTENT"
]
IGNOREOBJECTS = [
    "ADDITIONALATTRIBUTESCONTAINER",
    "ADDITIONALATTRIBUTENAME",
    "PARAMETERVALUE"
]

# Patterns for line sanitization
SANITIZEPAT = [
    (r'\s+=\s+', '='),
    (r'^\s+', ''),
    (r'\s+$', ''),
]

# A state machine is used to parse the file. There are 5 states (0 to 4):
STATUSCODE = [
    "begin",
    "enter metadata group",
    "add metadata item",
    "leave metadata group",
    "end"
    ]

# A custom exception for this module
class MTLParseError(Exception):
    """Custom exception: parse errors in Landsat or EO-1 MTL metadata files"""
    pass

def _deep_convert_dict(layer):
    """Helper function to convert dictionary back from OrderedDict"""
    to_ret = layer
    if isinstance(layer, OrderedDict):
        to_ret = dict(layer)
    try:
        for key, value in to_ret.items():
            to_ret[key] = _deep_convert_dict(value)
    except AttributeError:
        pass
    return to_ret

def _sanitizeline(line):
    for pattern, repl in SANITIZEPAT:
        line = re.sub(pattern, repl, line)
    return line

# Help functions to identify the current line and extract information
def _islinetype(line, testchar):
    """Checks for various kinds of line types based on line head"""
    return line.strip().startswith(testchar)

def _isassignment(line):
    """Checks if the line is a key-value assignment"""
    return ASSIGNCHAR in line

def _isfinal(line):
    """Checks if line finishes a group"""
    return line.strip() == FINAL

def _getgroupname(line):
    """Returns group name, if used with group start lines"""
    return line.strip().split(GRPSTART)[-1]

def _getendgroupname(line):
    """Returns group name, if used with group end lines"""
    return line.strip().split(GRPEND)[-1]

def _getobjname(line):
    """Returns object name, if used with object start lines"""
    return line.strip().split(OBJSTART)[-1]

def _getendobjname(line):
    """Returns group name, if used with group end lines"""
    return line.strip().split(OBJEND)[-1]


def _getmetadataitem(line):
    """Returns key/value pair for assignment type lines"""
    return line.strip().split(ASSIGNCHAR)

# After reading a line, what state we're in depends on the line
# and the state before reading
def _checkstatus(status, line):
    """Returns state/status after reading the next line.

    The status codes are::
        0 - BEGIN parsing; 1 - ENTER METADATA GROUP, 2 - READ KEY-VALUE PAIR,
        3 - END METDADATA GROUP, 4 - END PARSING, 5 - BEGIN OBJECT, 
        6 - END OBJECT

    Permitted Transitions::
        0 --> 1, 0 --> 4
        1 --> 1, 1 --> 2, 1 --> 3, 1 --> 5
        2 --> 1, 2 --> 2, 2 --> 3, 2 --> 5, 3 --> 6
        3 --> 1, 3 --> 2, 3 --> 4, 3 --> 5, 3 --> 6
        5 --> 1, 5 --> 2, 5 --> 5, 5 --> 6
        6 --> 1, 6 --> 2, 6 --> 5, 6 --> 6
        
    """
    newstatus = 0
    if status == 0:
        # begin --> enter metadata group OR end
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _isfinal(line):
            newstatus = 4
    elif status == 1:
        # enter metadata group --> enter metadata group
        # OR add metadata item OR leave metadata group
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, GRPEND):
            newstatus = 3
        elif _islinetype(line, OBJSTART):
            newstatus = 5
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    elif status == 2:
        if _islinetype(line, GRPEND):
            newstatus = 3
        elif _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, OBJSTART):
            newstatus = 5
        elif _islinetype(line, OBJEND):
            newstatus = 6
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
        elif _islinetype(line, OBJSTART):
            newstatus = 5
        elif _islinetype(line, OBJEND):
            newstatus = 6
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    elif status == 5:
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, GRPEND):
            newstatus = 3
        elif _islinetype(line, OBJSTART):
            newstatus = 5
        elif _islinetype(line, OBJEND):
            newstatus = 6
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    elif status == 6:
        if _islinetype(line, GRPSTART):
            newstatus = 1
        elif _islinetype(line, GRPEND):
            newstatus = 3
        elif _islinetype(line, OBJSTART):
            newstatus = 5
        elif _islinetype(line, OBJEND):
            newstatus = 6
        elif _isassignment(line):
            # test AFTER start and end, as both are also assignments
            newstatus = 2
    if newstatus != 0:
        return newstatus
    elif status != 4:
        raise MTLParseError(
            "Cannot parse the following line after status "
            + "'%s':\n%s" % (STATUSCODE[status], line))


def _transstat(status, grouppath, dictpath, line):
    """Executes processing steps when reading a line"""
    if status == 0:
        raise MTLParseError(
            "Status should not be '%s' after reading line:\n%s"
            % (STATUSCODE[status], line))
    elif status == 1:
        currentdict = dictpath[-1]
        currentgroup = _getgroupname(line)
        grouppath.append((currentgroup, 'g'))
        if currentgroup not in IGNOREGROUPS:
            currentdict[currentgroup] = OrderedDict()
            dictpath.append(currentdict[currentgroup])
    elif status == 2:
        currentdict = dictpath[-1]
        currentparent = grouppath[-1]
        newkey, newval = _getmetadataitem(line)
        if currentparent[1] == 'g':
            if currentparent[0] not in IGNOREGROUPS:
                currentdict[newkey] = _postprocess(newval)
        elif currentparent[1] == 'o':
            if newkey == 'VALUE':
                if currentparent[0] == "ADDITIONALATTRIBUTENAME":
                    currentdict[_postprocess(newval)] = None
                elif currentparent[0] == "PARAMETERVALUE":
                    curkey, curval = currentdict.popitem()
                    currentdict[curkey] = _postprocess(newval)
                else:
                    currentdict[currentparent[0]] = _postprocess(newval)
    elif status == 3:
        oldgroup = _getendgroupname(line)
        if oldgroup != grouppath[-1][0]:
            raise MTLParseError(
                "Reached line '%s' while reading group '%s'."
                % (line.strip(), grouppath[-1][0]))
        del grouppath[-1]
        if oldgroup not in IGNOREGROUPS:
            del dictpath[-1]
        try:
            currentgroup = grouppath[-1][0]
        except IndexError:
            currentgroup = None
    elif status == 4:
        if grouppath:
            raise MTLParseError(
                "Reached end before end of group '%s'" % grouppath[-1])
    elif status == 5:
        currentobj = _getobjname(line)
        grouppath.append((currentobj, 'o'))
    elif status == 6:
        oldobj = _getendobjname(line)
        if oldobj != grouppath[-1][0]:
            raise MTLParseError(
                "Reached line '%s' while reading object '%s'."
                % (line.strip(), grouppath[-1][0]))
        del grouppath[-1]
        try:
            currentobj = grouppath[-1][0]
        except IndexError:
            currentobj = None
    return grouppath, dictpath

# Identifying data type of a metadata item and
def _postprocess(valuestr):
    """
    Takes value as str, returns str, int, float, date, datetime, or time
    """
    intpattern = re.compile(r'^"?\-?\d+"?$')
    floatpattern = re.compile(r'^"?\-?\d+\.\d+(E[+-]?\d\d+)?"?$')
    datedtpattern = '%Y-%m-%d'
    datedttimepattern = '%Y-%m-%dT%H:%M:%SZ'
    timedtpattern = '%H:%M:%S.%f'
    timepattern = re.compile(r'^"?\d{2}:\d{2}:\d{2}(\.\d{6})?"?')

    # can we automatically parse it into something numeric?
    teststr = valuestr.replace("'", "").replace('"', "")
    try:
        return literal_eval(teststr.strip())
    except ValueError:
        pass   # try something else
    except SyntaxError:
        pass
    if re.match(intpattern, teststr):
        # it's an integer
        return int(teststr)
    elif re.match(floatpattern, teststr):
        # floating point number
        return float(teststr)
    # now let's try the datetime objects; throws exception if it doesn't match
    try:
        return datetime.datetime.strptime(teststr, datedtpattern).date()
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(teststr, datedttimepattern)
    except ValueError:
        pass
    # time parsing is complicated: Python's datetime module only accepts
    # fractions of a second only up to 6 digits
    mat = re.match(timepattern, teststr)
    if mat:
        test = mat.group(0)
        try:
            return datetime.datetime.strptime(test, timedtpattern).time()
        except ValueError:
            pass
    if valuestr.startswith('"') and valuestr.endswith('"'):
        # it's a string
            return valuestr[1:-1]
    
    # If we get here, we still haven't returned anything.
    logging.info(
        "The value %s couldn't be parsed as " % valuestr
        + "int, float, date, time, datetime. Returning it as string.")
    return valuestr

def parsemeta(metadataloc):
    """Parses the metadata.

    Arguments:
        metadataloc: a filename or a directory. Or a the string to 
        be parsed as an ODL block
    Returns metadata dictionary
    """

    # filename or directory? if several fit, use first one and warn
    if os.path.isdir(metadataloc):
        metalist = glob.glob(os.path.join(metadataloc, METAPATTERN))
        if not metalist:
            raise MTLParseError(
                "No files matching metadata file pattern in directory %s."
                % metadataloc)
        elif len(metalist) > 0:
            metadatastr = metalist[0]
            if len(metalist) > 1:
                logging.warning(
                    "More than one file in directory match metadata "
                    + "file pattern. Using %s." % metadatafn)
    else:
        metadatastr = metadataloc

    # Reading file line by line and inserting data into metadata dictionary
    try:
        with open(metadatastr, 'rU') as filehandle:
            metadata = _parsemetastream(filehandle)
    except IOError:
        # maybe the argument is a string. Converting to a file-like object
        logging.info("It's not a file, trying to open it as a string.")
        try:
            inpstream = StringIO(metadatastr)
        except:
            raise MTLParseError(
            "%s does not appear to be a file-like object " % metadatastr)
        metadata = _parsemetastream(inpstream)
    return _deep_convert_dict(metadata)

def _parsemetastream(filehandle):
    status = 0
    metadata = OrderedDict()
    grouppath = []
    dictpath = [metadata]
    for line in filehandle:
        line = _sanitizeline(line)
        if not line:
            continue
        if status == 4:
            # we reached the end in the previous iteration,
            # but are still reading lines
            logging.warning(
                "Metadata file %s appears to " % metadatafn
                + "have extra lines after the end of the metadata. "
                + "This is probably, but not necessarily, harmless.")
        status = _checkstatus(status, line)
        grouppath, dictpath = _transstat(status, grouppath, dictpath, line)
    return metadata