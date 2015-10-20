__author__ = 'ryan'

import collections
from db.ODM1.ODM1 import ODM1
import xml.etree.ElementTree as et

class WebServiceApi:

    def __init__(self, website):

        self.odm1 = ODM1(website)
        self.objects = self.odm1.getSitesObject()

    def buildSitesDictionary(self, start=None, end=None):

        if start == None:
            start = 1
        if end  == None:
            end = start + 10

        siteInfo_Dictionary = collections.OrderedDict()
        for site in self.objects[1][start:end]:
            if len(site) > 0:
                siteInfo_Dictionary[site[0][0]] = site[0][1][0][0]

        return siteInfo_Dictionary

    def buildAllVariableDictionary(self, start=None, end=None):

        if start == None:
            start = 1
        if end == None:
            end = start + 10

        xml = self.odm1.getVariables()
        self.odm1.createXMLFileForReading(xml)
        vars = self.odm1.parseXML2Dict(xml, start, end)
        vars = iter(vars)
        next(vars)
        self.AllVariables = vars
        return vars

    def buildAllSiteCodeVariables(self, sitecode, start=None, end=None):
        if start is None:
            start = 1
        if end is None:
            end = start + 10

        siteObject = self.odm1.getSiteInfoObject(sitecode)

        try:
            seriesVariables = siteObject[1][0][1][0][2]
        except Exception as e:
            print e  # There exist no variables
            return {}

        variableDict = collections.OrderedDict()

        for i in range(0, len(seriesVariables[start:end])):
            # {Site code: [Variable Name, Units, Type, Category, Begin Date Time, End Date Time, Description]}
            variableDict[seriesVariables[i][0][0][0].value] = [seriesVariables[i][0][1],  # Variable Name
                                                               seriesVariables[i][0][6][2],  # Units
                                                               seriesVariables[i][0][3],  # Type
                                                               seriesVariables[i][0][4],  # Category
                                                               seriesVariables[i][2][0],  # Begin Date Time Objects
                                                               seriesVariables[i][2][1],  # End Date Time Objects
                                                               seriesVariables[i][3][1],  # Description
                                                               ]
        return variableDict

    def buildSiteVariables(self, siteCode):

        self.siteVarables = collections.OrderedDict()

    def getSiteInfo(self, start=None, end=None):

        if start == None:
            start = 0
        if end  == None:
            end = start + 9

        siteInfo = []
        for site in self.objects[1][start:end]:
            if len(site) > 0:
                # The structure of siteInfo list is [[Site Name, County, State, site code]]
                siteInfo.append([site[0][0], site[0][5][0].value, site[0][5][1].value, site[0][1][0].value])

        return siteInfo

    def parseValues(self, sitecode, variable, start=None, end=None):
        # Data is taken every 15 minutes
        # start date can be as early as 2013
        # end data is today and continuing.
        # There are 96 values for each day.

        data = self.odm1.getValues(sitecode, variable, start, end)
        tree = et.fromstring(data)
        valuesList = []

        queryInfo = tree[0]
        sourceInfo = tree[1].getchildren()[0]
        varInfo = tree[1].getchildren()[1]
        values = tree[1].getchildren()[2]
        stop = len(values) - 4

        # self.odm1.createXMLFileForReading(data) Run this line to see the file in your browser

        if start is not None and end is not None:
            for i in range(stop):
                valuesList.append(values[i].text)

        else:  # Below will be an example of grabbing the data points for the most recent 2 days.
            for i in range(stop-(2*96), stop):
                valuesList.append(values[i].text)

        return valuesList
