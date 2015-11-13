#!/usr/bin/env python
# encoding: utf-8
"""
**Module pygaarst.modapsclient**

**A client to do talk to MODAPS web services.
See http://ladsweb.nascom.nasa.gov/data/web_services.html**

*Created by Chris Waigl on 2013-10-22.*
"""

from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import urllib, urllib2
from xml.dom import minidom

import logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger('pygaarst.modapsclient')

MODAPSBASEURL = u"http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices"

def _parsekeyvals(domobj, containerstr, keystr, valstr):
    """Parses what's basically a keys-values structrue in a list of container
    elements of the form
    <container><key>A_KEY</key><value>A_VALUE</value></container>
    and returns it as a dictionary"""
    output = {}
    nodelist = domobj.getElementsByTagName(containerstr)
    for node in nodelist:
        key = value = None
        children = node.childNodes
        for child in children:
            if child.tagName == keystr:
                key = child.firstChild.data
            elif child.tagName == valstr:
                value = child.firstChild.data
        if key and value:
            output[key] = value
    return output

def _parselist(domobj, containerstr):
    """Parses what's basically a list of strings contained in a container
    elements of the form
    <container>A_VALUE</container>
    and returns it as a list"""
    output = []
    nodelist = domobj.getElementsByTagName(containerstr)
    for node in nodelist:
        output.append(node.firstChild.data)
    return output

def _parselistofdicts(domobj, containerstr, prefix, listofkeys):
    """Parses what's basically a list of dictionaries contained in a container
    elements of the form
    <container><prefix:key1>VAL1</prefix:key1><prefix:key2>...
    </prefix:key2>...</container>
    and returns it as a list of dictionaries"""
    output = []
    nodelist = domobj.getElementsByTagName(containerstr)
    for node in nodelist:
        item = {}
        children = node.childNodes
        for child in children:
            if child.tagName.startswith(prefix):
                key = child.tagName.replace(prefix, '', 1)
                item[key] = child.firstChild.data
        output.append(item)
    return output

def _startswithax(item):
    """
    Helper function to filter tag lists for starting with xmlns:ax
    """
    return item.startswith('xmlns:ax')

class ModapsClient(object):
    """
    Implements a client for MODAPS web service retrieval of satellite data,
    without post-processing

    See http://ladsweb.nascom.nasa.gov/data/quickstart.html
    """

    def __init__(self):
        self.baseurl = MODAPSBASEURL
        self.headers = {
            u'User-Agent': u'satellite RS data fetcher'
            }

    def _parsedresponse(self, path, argdict, parserfun,
                        data=None, unstabletags=False):
        """Returns response based on request and parser function"""
        url = self.baseurl + path
        if data:
            querydata = urllib.urlencode(data)
            request = urllib2.Request(url, querydata, headers=self.headers)
        else:
            request = urllib2.Request(url, headers=self.headers)
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as err:
            logging.critical("Error opening URL: %s" % err)
            logging.critical("URL is %s" % url)
            if data:
                logging.critical("Query string is %s" % querydata)
            sys.exit(1)
        xmldoc = minidom.parseString(response)
        if unstabletags:
            attr = xmldoc.documentElement.attributes.items()
            pref = filter(_startswithax, [item[0] for item in attr])
            if not pref:
                LOGGER.error(
                    "No valid namespace prefix found for request %s ." % url)
                sys.exit(1)
            elif len(pref) > 1:
                LOGGER.error(
                    "Too many potential namespace prefix found for "
                    + "request %s. Using %s." % (url, pref[0]))
            else:
                prefix = pref[0][6:] + ':'
                for item in argdict:
                    if item != 'containerstr':
                        argdict[item] = prefix + argdict[item]
        return parserfun(xmldoc, **argdict)

    def getAllOrders(self, email):
        """All orders for an email address"""
        pass

    def getBands(self, product):
        """Available bands for a product"""
        path = u'/getBands'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'keystr'] = u'mws:name'
        argdict[u'valstr'] = u'mws:value'
        data = {}
        data[u'product'] = product
        return self._parsedresponse(path, argdict, parser, data=data)

    def getBrowse(self, fileId):
        """fileIds is a single file-ID"""
        path = u'/getBrowse'
        parser = _parselistofdicts
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'prefix'] = u'mws:'
        argdict[u'listofkeys'] = [
            u'fileID', u'product', u'description'
            ]
        data = {}
        data[u'fileId'] = fileId
        return self._parsedresponse(path, argdict, parser, data=data)

    def getCollections(self, product):
        """Available collections for a product"""
        path = u'/getCollections'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'mws:Collection'
        argdict[u'keystr'] = u'mws:Name'
        argdict[u'valstr'] = u'mws:Description'
        data = {}
        data[u'product'] = product
        return self._parsedresponse(path, argdict, parser, data=data)

    def getDataLayers(self, product):
        """Available data layers for a product"""
        path = u'/getDataLayers'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'keystr'] = u'mws:name'
        argdict[u'valstr'] = u'mws:value'
        data = {}
        data[u'product'] = product
        return self._parsedresponse(path, argdict, parser, data=data)

    def getDateCoverage(self, collection, product):
        '''Available dates for a collection/product combination

        TODO: add some result postprocessing - not a good format'''
        path = u'/getDateCoverage'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'product'] = product
        data[u'collection'] = collection
        return self._parsedresponse(path, argdict, parser, data=data)

    def getFileOnlineStatuses(self, fileIds):
        """fileIds is a comma-separated list of file-IDs"""
        path = u'/getFileOnlineStatuses'
        parser = _parselistofdicts
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'prefix'] = u'mws:'
        argdict[u'listofkeys'] = [
            u'fileID', u'archiveAutoDelete', u'requireUntil'
            ]
        data = {}
        data[u'fileIds'] = fileIds
        return self._parsedresponse(path, argdict, parser, data=data)

    def getFileProperties(self, fileIds):
        """fileIds is a comma-separated list of file-IDs"""
        path = u'/getFileProperties'
        parser = _parselistofdicts
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'prefix'] = u'mws:'
        argdict[u'listofkeys'] = [
            u'fileID', u'fileName', u'checksum', u'fileSizeBytes',
            u'fileType', u'ingestTime', u'online', u'startTime'
            ]
        data = {}
        data[u'fileIds'] = fileIds
        return self._parsedresponse(path, argdict, parser, data=data)

    def getFileUrls(self, fileIds):
        """fileIds is a comma-separated list of file-IDs"""
        path = u'/getFileUrls'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'fileIds'] = fileIds
        return self._parsedresponse(path, argdict, parser, data=data)

    def getMaxSearchResults(self):
        """Max number of search results that can be returned"""
        path = u'/getMaxSearchResults'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'ns:return'
        return self._parsedresponse(path, argdict, parser)

    def getOrderStatus(self, OrderID):
        """Order status for an order ID. TODO: implement"""
        pass

    def getOrderUrl(self, OrderID):
        """Order URL(?) for order ID. TODO: implement"""
        pass

    def getPostProcessingTypes(self, products):
        '''Products: comma-concatenated string of valid product labels'''
        path = u'/getPostProcessingTypes'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'products'] = products
        return self._parsedresponse(path, argdict, parser, data=data)

    def listCollections(self):
        """Lists all collections. Deprecated: use getCollections"""
        path = u'/listCollections'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'ns:return'
        argdict[u'keystr'] = u'id'
        argdict[u'valstr'] = u'value'
        return self._parsedresponse(path, argdict, parser, unstabletags=True)

    def listMapProjections(self):
        """Lists all available map projections"""
        path = u'/listMapProjections'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'ns:return'
        argdict[u'keystr'] = u'name'
        argdict[u'valstr'] = u'value'
        return self._parsedresponse(path, argdict, parser, unstabletags=True)

    def listProductGroups(self, instrument):
        """Lists all available product groups"""
        path = u'/listProductGroups'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'keystr'] = u'mws:name'
        argdict[u'valstr'] = u'mws:value'
        data = {}
        data[u'instrument'] = instrument
        return self._parsedresponse(path, argdict, parser, data=data)

    def listProducts(self):
        """Lists all available products"""
        path = u'/listProducts'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'mws:Product'
        argdict[u'keystr'] = u'mws:Name'
        argdict[u'valstr'] = u'mws:Description'
        return self._parsedresponse(path, argdict, parser)

    def listProductsByInstrument(self, instrument, group=None):
        """Lists all available products for an instrument"""
        path = u'/listProductsByInstrument'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'instrument'] = instrument
        if group:
            data[u'group'] = group
        return self._parsedresponse(path, argdict, parser, data=data)

    def listReprojectionParameters(self, reprojectionName):
        """Lists reprojection parameters for a reprojection"""
        path = u'/listReprojectionParameters'
        parser = _parselistofdicts
        argdict = {}
        argdict[u'containerstr'] = u'return'
        argdict[u'prefix'] = u'mws:'
        argdict[u'listofkeys'] = [
            u'name', u'description', u'units'
            ]
        data = {}
        data[u'reprojectionName'] = reprojectionName
        return self._parsedresponse(path, argdict, parser, data=data)

    def listSatelliteInstruments(self):
        """Lists all available satellite instruments"""
        path = u'/listSatelliteInstruments'
        parser = _parsekeyvals
        argdict = {}
        argdict[u'containerstr'] = u'ns:return'
        argdict[u'keystr'] = u'name'
        argdict[u'valstr'] = u'value'
        return self._parsedresponse(path, argdict, parser, unstabletags=True)

    def orderFiles(self, FileIDs):
        """Submits an order. TODO: implement"""
        pass

    def searchForFiles(
            self, products, startTime, endTime,
            north, south, east, west,
            coordsOrTiles=u'coords',
            dayNightBoth=u'DNB', collection=5):
        """Submits a search based on product, geography and time"""
        path = u'/searchForFiles'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'products'] = products
        data[u'startTime'] = startTime
        data[u'endTime'] = endTime
        data[u'north'] = north
        data[u'south'] = south
        data[u'east'] = east
        data[u'west'] = west
        data[u'coordsOrTiles'] = coordsOrTiles
        if collection:
            data[u'collection'] = collection
        if dayNightBoth:
            data[u'dayNightBoth'] = dayNightBoth
        return self._parsedresponse(path, argdict, parser, data=data)

    def searchForFilesByName(self, collection, pattern):
        """Submits a search based on a file name pattern"""
        path = u'/searchForFilesByName'
        parser = _parselist
        argdict = {}
        argdict[u'containerstr'] = u'return'
        data = {}
        data[u'collection'] = collection
        data[u'pattern'] = pattern
        return self._parsedresponse(path, argdict, parser, data=data)

if __name__ == '__main__':
    a = ModapsClient()
    req = a.listCollections()
    print(req)
