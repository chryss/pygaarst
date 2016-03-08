#!/usr/bin/env python
# encoding: utf-8
"""
test_mtlutils.py

Created by Chris Waigl on 2013-11-10.
"""

from __future__ import division, print_function, absolute_import
import os, os.path
import pytest
from pygaarst import mtlutils as mtl

DATADIR = "tests/data"
MODL2meta = """

GROUP                  = INVENTORYMETADATA
  GROUPTYPE            = MASTERGROUP

  GROUP                  = ECSDATAGRANULE

    OBJECT                 = LOCALGRANULEID
      NUM_VAL              = 1
      VALUE                = "MOD021KM.A2015167.0805.005.2015170121435.hdf"
    END_OBJECT             = LOCALGRANULEID

    OBJECT                 = PRODUCTIONDATETIME
      NUM_VAL              = 1
      VALUE                = "2015-06-19T12:14:36.000Z"
    END_OBJECT             = PRODUCTIONDATETIME

    OBJECT                 = DAYNIGHTFLAG
      NUM_VAL              = 1
      VALUE                = "Both"
    END_OBJECT             = DAYNIGHTFLAG

    OBJECT                 = REPROCESSINGACTUAL
      NUM_VAL              = 1
      VALUE                = "processed once"
    END_OBJECT             = REPROCESSINGACTUAL

    OBJECT                 = REPROCESSINGPLANNED
      NUM_VAL              = 1
      VALUE                = "further update is anticipated"
    END_OBJECT             = REPROCESSINGPLANNED

  END_GROUP              = ECSDATAGRANULE

  GROUP                  = ANCILLARYINPUTGRANULE

    OBJECT                 = ANCILLARYINPUTGRANULECONTAINER
      CLASS                = "1"

      OBJECT                 = ANCILLARYINPUTPOINTER
        CLASS                = "1"
        NUM_VAL              = 1
        VALUE                = "MOD03.A2015167.0805.005.2015170114131.hdf"
      END_OBJECT             = ANCILLARYINPUTPOINTER

      OBJECT                 = ANCILLARYINPUTTYPE
        CLASS                = "1"
        NUM_VAL              = 1
        VALUE                = "Geolocation"
      END_OBJECT             = ANCILLARYINPUTTYPE

    END_OBJECT             = ANCILLARYINPUTGRANULECONTAINER

  END_GROUP              = ANCILLARYINPUTGRANULE


  GROUP                  = ADDITIONALATTRIBUTES

    OBJECT                 = ADDITIONALATTRIBUTESCONTAINER
      CLASS                = "1"

      OBJECT                 = ADDITIONALATTRIBUTENAME
        CLASS                = "1"
        NUM_VAL              = 1
        VALUE                = "AveragedBlackBodyTemperature"
      END_OBJECT             = ADDITIONALATTRIBUTENAME

      GROUP                  = INFORMATIONCONTENT
        CLASS                = "1"

        OBJECT                 = PARAMETERVALUE
          NUM_VAL              = 1
          CLASS                = "1"
          VALUE                = " 290.01"
        END_OBJECT             = PARAMETERVALUE

      END_GROUP              = INFORMATIONCONTENT

    END_OBJECT             = ADDITIONALATTRIBUTESCONTAINER

    OBJECT                 = ADDITIONALATTRIBUTESCONTAINER
      CLASS                = "2"

      OBJECT                 = ADDITIONALATTRIBUTENAME
        CLASS                = "2"
        NUM_VAL              = 1
        VALUE                = "AveragedMirrorTemperature"
      END_OBJECT             = ADDITIONALATTRIBUTENAME

      GROUP                  = INFORMATIONCONTENT
        CLASS                = "2"

        OBJECT                 = PARAMETERVALUE
          NUM_VAL              = 1
          CLASS                = "2"
          VALUE                = " 277.85"
        END_OBJECT             = PARAMETERVALUE

      END_GROUP              = INFORMATIONCONTENT

    END_OBJECT             = ADDITIONALATTRIBUTESCONTAINER

   END_GROUP              = ADDITIONALATTRIBUTES

END_GROUP              = INVENTORYMETADATA

END
"""

def setup_module(module):
    mydir = DATADIR
    metadatapath8 = os.path.join(mydir, "LC8_test", "LC8_test_MTL.txt")
    global metadatapaths
    metadatapaths = [
        metadatapath8, 
#        datapath7, datapath51, datapath52
    ]

def test_file():
    for p in metadatapaths:
        a = os.path.isfile(p)
        assert a

def test_read_metadata_L8():
    meta = mtl.parsemeta(metadatapaths[0])
    assert meta['L1_METADATA_FILE']['PRODUCT_METADATA']['SPACECRAFT_ID']  == 'LANDSAT_8'
    assert meta['L1_METADATA_FILE']['METADATA_FILE_INFO']['PROCESSING_SOFTWARE_VERSION'] == 'LPGS_2.2.2'

def test_read_MODL2_metadata_from_string():
    meta = mtl.parsemeta(MODL2meta)
    assert meta["INVENTORYMETADATA"]["ANCILLARYINPUTGRANULE"]["ANCILLARYINPUTPOINTER"] == 'MOD03.A2015167.0805.005.2015170114131.hdf'
    assert meta["INVENTORYMETADATA"]["ADDITIONALATTRIBUTES"]["AveragedBlackBodyTemperature"] == 290.01
    assert len(meta["INVENTORYMETADATA"]) == 4
