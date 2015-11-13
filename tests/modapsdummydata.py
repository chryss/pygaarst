modapsresponses = {
    '/getFileUrls': """<mws:getFileUrlsResponse xmlns:mws="http://modapsws.gsfc.nasa.gov/xsd">
<return>
ftp://ladsweb.nascom.nasa.gov/allData/5/MOD021KM/2004/201/MOD021KM.A2004201.2130.005.2010141190341.hdf
</return>
</mws:getFileUrlsResponse>""",
    '/GetBrowse': """<mws:getBrowseResponse xmlns:mws="http://modapsws.gsfc.nasa.gov/xsd">
<return mws:type="mws:BrowseFile">
<mws:fileId>1408022673</mws:fileId>
<mws:product>MYBRGB</mws:product>
<mws:description>Aqua Granule Level 1 browse RGB FROM MYD021KM</mws:description>
</return>
</mws:getBrowseResponse>""",
    '/searchForFiles':"""<mws:searchForFilesResponse xmlns:mws="http://modapsws.gsfc.nasa.gov/xsd">
<return>204846513</return>
<return>204718831</return>
<return>204717651</return>
<return>204732495</return>
<return>204732383</return>
<return>204732285</return>
<return>204733820</return>
</mws:searchForFilesResponse>""",
    '/listSatelliteInstruments': """<ns:listSatelliteInstrumentsResponse xmlns:ns="http://laads.modapsws.gsfc.nasa.gov" xmlns:ax21="http://datatypes.laads.modapsws.gsfc.nasa.gov/xsd"><ns:return xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ax21:NameValuePair"><ax21:name>AM1M</ax21:name><ax21:value>Terra MODIS</ax21:value></ns:return><ns:return xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ax21:NameValuePair"><ax21:name>ANC</ax21:name><ax21:value>Ancillary Data</ax21:value></ns:return><ns:return xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ax21:NameValuePair"><ax21:name>PM1M</ax21:name><ax21:value>Aqua MODIS</ax21:value></ns:return><ns:return xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ax21:NameValuePair"><ax21:name>AMPM</ax21:name><ax21:value>Combined Aqua &amp; Terra MODIS</ax21:value></ns:return><ns:return xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ax21:NameValuePair"><ax21:name>NPP</ax21:name><ax21:value>Suomi NPP VIIRS</ax21:value></ns:return></ns:listSatelliteInstrumentsResponse>""",
    '/getDataLayers': """<mws:getDataLayersResponse xmlns:mws="http://modapsws.gsfc.nasa.gov/xsd">
<return mws:type="mws:NameValuePair">
<mws:name>
MOD021KM___DC Restore Change for Reflective 1km Bands
</mws:name>
<mws:value>DC Restore Change for Reflective 1km Bands</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___EV_1KM_Emissive_Uncert_Indexes</mws:name>
<mws:value>Earth View 1KM Emissive Bands Uncertainty Indexes</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___EV_Band26_Uncert_Indexes</mws:name>
<mws:value>Earth View Band 26 Uncertainty Indexes</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___EV_1KM_RefSB_Uncert_Indexes</mws:name>
<mws:value>
Earth View 1KM Reflective Solar Bands Uncertainty Indexes
</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___SensorZenith</mws:name>
<mws:value>SensorZenith</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___Band_250M</mws:name>
<mws:value>250M Band Numbers for Subsetting</mws:value>
</return>
</mws:getDataLayersResponse>""",
    '/getBands': """<mws:getBandsResponse xmlns:mws="http://modapsws.gsfc.nasa.gov/xsd">
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___1</mws:name>
<mws:value>1</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___2</mws:name>
<mws:value>2</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___3</mws:name>
<mws:value>3</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___4</mws:name>
<mws:value>4</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___5</mws:name>
<mws:value>5</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___6</mws:name>
<mws:value>6</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___7</mws:name>
<mws:value>7</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___8</mws:name>
<mws:value>8</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___9</mws:name>
<mws:value>9</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___10</mws:name>
<mws:value>10</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___11</mws:name>
<mws:value>11</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___12</mws:name>
<mws:value>12</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___13lo</mws:name>
<mws:value>13 - Lo</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___13hi</mws:name>
<mws:value>13 - High</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___14lo</mws:name>
<mws:value>14 - Lo</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___14hi</mws:name>
<mws:value>14 - High</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___15</mws:name>
<mws:value>15</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___16</mws:name>
<mws:value>16</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___17</mws:name>
<mws:value>17</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___18</mws:name>
<mws:value>18</mws:value>
</return>
<return mws:type="mws:NameValuePair">
<mws:name>MOD021KM___19</mws:name>
<mws:value>19</mws:value>
</return>
</mws:getBandsResponse>""",
    'invalid': """<soapenv:Reason xmlns:soapenv="http://www.w3.org/2003/05/soap-envelope">
<soapenv:Text xml:lang="en-US">
The endpoint reference (EPR) for the Operation not found is /axis2/services/MODAPSservices/listSatelliteInstrument and the WSA Action = null
</soapenv:Text>
</soapenv:Reason>"""
}