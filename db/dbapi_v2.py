import datetime
import time
import uuid

# import apsw as sqlite3
import numpy
import sqlalchemy
from odm2api.ODM2 import models
from odm2api.ODM2.services.createService import CreateODM2
from odm2api.ODM2.services.deleteService import DeleteODM2
from odm2api.ODM2.services.readService import ReadODM2
from odm2api.ODM2.services.updateService import UpdateODM2
from sqlalchemy.orm import class_mapper

from sprint import *
# This is our API for simulation data that uses the latest ODM2PythonAPI code


from emitLogging import elog

def connect(sessionFactory):

    driver = sessionFactory.engine.url.drivername

    if 'sqlite' in driver:
        return sqlite(sessionFactory)

    # todo: implement MsSQL in dbapi_v2
    elif 'mssql' in driver:
        elog.error('MsSQL not supported yet')
        return None

    # todo: implement postgres in dbapi_v2
    elif 'postgresql' in driver:
        return postgres(sessionFactory)
        # elog.error('PostgreSQL not supported yet')
        # return None

    # todo: implement mysql in dbapi_v2
    elif 'mysql' in driver:
        elog.error('MySQL not supported yet')
        return None



class sqlite():

    def __init__(self, session):


        # build sqlalchemy connection
        # self.connection = dbconnection.createConnection('sqlite', sqlitepath)
        self.connection = session
        sqlitepath = session.engine.url.database

        # create read, write, update, and delete ODM2PythonAPI instances
        self.read = ReadODM2(self.connection)
        self.write = CreateODM2(self.connection)
        self.update = UpdateODM2(self.connection)
        self.delete = DeleteODM2(self.connection)

        # create connection using spatialite for custom sql queries
        self.conn = sqlite3.Connection(sqlitepath)
        self.cursor = self.conn.cursor()

        # load mod_spatialite extension
        self.conn.enableloadextension(True)
        try:
            self.cursor.execute('SELECT load_extension("mod_spatialite")')
        except Exception, e:
            elog.error('Encountered and error when attempting to load mod_spatialite: %s' % e)
            sPrint('Could not load mod_spatialite.  Your database will not be geo-enabled', MessageType.WARNING)


    def get_next_insert_id(self, cls):

        # get the column attributes for the table
        atts = [prop.key for prop in class_mapper(cls).iterate_properties
                if isinstance(prop, sqlalchemy.orm.ColumnProperty)]


        # get the table name
        clsname = None
        for classname in cls._decl_class_registry:
            if classname.lower() == cls.__tablename__:
                clsname = classname
                break

        # query the objects in this table
        res = self.cursor.execute('SELECT {} FROM {} ORDER BY {} DESC'.format(atts[0], clsname, atts[0]))

        # return the next insert it
        lastID = res.fetchone() or (-1,)
        nextID = lastID[0] + 1 # increment the last id
        return nextID

    def create_user(self, userInfo):
        person = self.write.createPerson(userInfo['firstName'], userInfo['lastName'])
        return person.PersonID

    def create_organization(self, organInfo):
        org = self.write.createOrganization(organInfo['cvType'], organInfo['code'], organInfo['name'],
                                            organInfo['desc'], organInfo['link'], organInfo['parentOrgId'])
        return org.OrganizationID

    def create_input_dataset(self, connection, resultids,type,code="",title="",abstract=""):
        pass

    def create_simulation(self, coupledSimulationName, user_obj, config_params, ei, simulation_start, simulation_end, timestep_value, timestep_unit, description, name):
        """
        Inserts a simulation record into the database
        Args:
            coupledSimulationName: The name of the coupled model simulation
            user_obj: object containing the user
            config_params:
            ei:
            simulation_start:
            simulation_end:
            timestep_value:
            timestep_unit:
            description:
            name:

        Returns:

        """
        bench_insert_fa = 0


        # todo: handle multiple affiliations
        person = self.createPerson(user_obj)
        organization = self.createOrganization(user_obj)
        affiliation = self.createAffiliation(organization.OrganizationID, person.PersonID, user_obj)

        # get the timestep unit id
        timestepunit = self.createTimeStepUnit(timestep_unit, timestep_unit)

        # insert method
        method = self.createMethod(organization)

        # # insert action
        # # todo: this is broken in the odm2api.  See issue #67: https://github.com/ODM2/ODM2PythonAPI/issues/67
        # ab = models.ActionBy()
        # ab.AffiliationID = affiliation[0].AffiliationID
        # ab.IsActionLead = True
        # a = models.Actions()
        # a.ActionTypeCV = 'Simulation'
        # a.MethodID = method.MethodID
        # a.BeginDateTime = datetime.datetime.now()
        # a.BeginDateTimeUTCOffset = int((datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds()/3600)
        # self.write.createAction(a, ab)
        # actions = self.read.getActions(type=a.ActionTypeCV)
        # action = actions[0]


        # create processing level
        processinglevels = self.read.getProcessingLevels(codes=[2])
        if not processinglevels:
            pl = models.ProcessingLevels()
            pl.ProcessingLevelCode = 2
            pl.Definition = 'Derived Product'
            pl.Explanation ='Derived products require scientific and technical interpretation and include multiple-sensor data. An example might be basin average precipitation derived from rain gages using an interpolation procedure.'
            self.write.createProcessingLevel(pl)
            processinglevels = self.read.getProcessingLevels(codes=[2])
        processinglevel = processinglevels[0]

        # create dataset
        ds = models.DataSets()
        ds.DataSetAbstract = description
        ds.DataSetTitle = 'Input for Simulation : %s' % name
        ds.DataSetCode = 'Input_%s' % name
        ds.DataSetTypeCV = 'Simulation Input'
        ds.DataSetUUID = uuid.uuid4().hex
        self.write.createDataset(ds)
        datasets = self.read.getDataSets(codes=[ds.DataSetCode])
        dataset = datasets[0]


        # make sure the exchange item is represented as a list
        if not hasattr(ei,'__len__'):
            ei = [ei]

        # loop over output exchange items
        for e in ei:

            geometries = numpy.array(e.getGeometries2())
            dates = numpy.array(e.getDates2())
            datavalues = numpy.array( e.getValues2())

            # create variable
            # TODO: This is not correct!
            # todo: implement variable vType
            variables = self.read.getVariables(e.variable().VariableNameCV())
            if not variables:
                v = models.Variables()
                v.VariableCode = e.variable().VariableNameCV()
                v.VariableNameCV = e.variable().VariableDefinition()
                v.VariableTypeCV = 'unknown'
                v.NoDataValue = -999
                self.write.createVariable(v)
                variables = self.read.getVariables(e.variable().VariableNameCV())
            variable = variables[0]

            # # variable = self.read.getVariableByCode(e.variable().VariableNameCV())
            # if not variable: variable = self.write.createVariable(code=e.variable().VariableNameCV(),
            #                                                       name=e.variable().VariableDefinition(),
            #                                                       vType='unknown',
            #                                                       nodv=-999)

            # # create unit
            # unit = self.read.getUnitByName(e.unit().UnitName())
            # if not unit:
            #     unit = self.write.createUnit(type=e.unit().UnitTypeCV(), abbrev=e.unit().UnitAbbreviation(),  name=e.unit().UnitName())

            unit = self.read.getUnits(name=e.unit().UnitName())
            if not unit:
                u = models.Units()
                u.UnitsAbbreviation = e.unit().UnitAbbreviation
                u.UnitsName = e.unit().UnitName()
                u.UnitsTypeCV = e.unit().UnitTypeCV()
                self.write.createUnit(u)
                unit = self.read.getUnits(name=e.unit().UnitName())

            # create spatial reference
            srs = e.srs()
            refcode = "%s:%s" %(srs.GetAttrValue("AUTHORITY", 0), srs.GetAttrValue("AUTHORITY", 1))
            # spatialref = self.read.getSpatialReferenceByCode(refcode)
            # if not spatialref:
            #     spatialref = self.write.createSpatialReference(srsCode=refcode,
            #                                                    srsName=srs.GetAttrValue("GEOGCS", 0),
            #                                                    srsDescription="%s|%s|%s"%(srs.GetAttrValue("PROJCS", 0),
            #                                                                               srs.GetAttrValue("GEOGCS", 0),
            #                                                                               srs.GetAttrValue("DATUM", 0)))
            spatialrefs = self.read.getSpatialReference(srsCodes=[refcode])
            if not spatialrefs:
                sr = models.SpatialReferences()
                sr.SRSCode = refcode
                sr.SRSName = srs.GetAttrValue("GEOGCS", 0)
                sr.SRSDescription = "%s|%s|%s" % (srs.GetAttrValue("PROJCS", 0), srs.GetAttrValue("GEOGCS", 0), srs.GetAttrValue("DATUM", 0))
                self.write.createSpatialReference(sr)
                spatialrefs = self.read.getSpatialReference(srsCodes=[refcode])
            spatialref = spatialrefs[0]


            st = time.time()
            samplingfeaturesids = []
            for i in range(0, len(geometries)):
                # create sampling features
                geom_wkt = geometries[i].ExportToWkt()
                geom_type = geometries[i].type
                samplingFeature = self.getSamplingFeatureID__Geometry_EQUALS(geom_wkt)
                if not samplingFeature:
                    samplingFeature = self.insert_sampling_feature(type='site',geometryType=geom_type, WKTgeometry=geom_wkt)
                samplingfeaturesids.append(samplingFeature.SamplingFeatureID)
            bench_insert_sf = (time.time() - st)
            sPrint('Inserting Sampling Features (not bulk) %3.5f sec' % bench_insert_sf, MessageType.INFO)

            st = time.time()
            featureactions = []
            action_ids = [action.ActionID] * len(samplingfeaturesids)
            featureactionids = self.insert_feature_actions_bulk(samplingfeaturesids, action_ids)
            bench_insert_fa += (time.time() - st)
            sPrint('Inserting Feature Actions (bulk) %3.5f sec' % bench_insert_fa, MessageType.INFO)

            st = time.time()
            resultids = self.insert_results_bulk(FeatureActionIDs=featureactionids, ResultTypeCV='time series', VariableID=variable.VariableID,
                                     UnitsID=unit.UnitsID, ValueCount=len(dates), ProcessingLevelID=processinglevel.ProcessingLevelID,
                                                 SampledMediumCV='unknown')
            sPrint('Inserting Results (bulk) %3.5f sec' % (time.time() - st), MessageType.INFO)

            for resultid in resultids:

                # hack: this is necessary since createTimeSeries requires a Result object. This can be removed when the function is fixed
                resultObj = models.Results
                resultObj.ResultID = resultid

                # create time series result
                st = time.time()
                tsr = self.write.createTimeSeriesResult(resultObj, aggregationstatistic='Unknown')
                # self.insert_timeseries_results_bulk(resultIDs=resultid, timespacing=timestep_value, timespacing_unitid=timestepunit.UnitsID)
                sPrint('Inserting Timeseries Results %3.5f sec' % (time.time() - st), MessageType.INFO)

                values = datavalues.flatten(order='C') # flatten row-wise, [t1g1, t1g2, ..., t1gn, t2g1, t2g2, ..., t2gn, ...]
                valuedates = dates[:,1]  # get all rows of the datetime column of the dates array [t1, t2, t3, ..., tn]
                flattened_ids = []
                flattened_dates = []
                geom_count = len(geometries)

                for dt in valuedates:
                    flattened_dates.extend([dt] * geom_count)  # [t1, t1, ..., t1, t2, t2, ..., t2, tn, tn, ..., tn]

                # for i in range(geom_count):
                #     flattened_ids.extend(resultids)     # [id1, id2, ..., idn, id1, id2, ..., idn, ...]

                st = time.time()
                try:
                    self.insert_timeseries_result_values_bulk(ResultIDs=resultid,
                                                              TimeAggregationInterval=timestep_value,
                                                              TimeAggregationIntervalUnitsID=timestepunit.UnitsID,
                                                              DataValues=values, ValueDateTimes=flattened_dates,
                                                              ValueDateTimeUTCOffset=-6, CensorCodeCV='nc',
                                                              QualityCodeCV='unknown')
                    bulk = time.time() - st
                    sPrint('Bulk Inserting Timeseries Results Values (%d records)... %3.5f seconds' % (
                    len(values), bulk), MessageType.INFO)

                except Exception, e:
                    msg = 'Encountered an error while inserting timeseries result values: %s' %e
                    elog.error(msg)
                    sPrint(msg, MessageType.ERROR)
                    return None




        # create the model instance
        model = self.createModel(name, description, name)

        # create simulation
        # TODO: remove hardcoded time offsets!
        sim = self.write.createSimulation(actionid=action.ActionID,
                                          modelID=model.ModelID,
                                          simulationName=coupledSimulationName,
                                          simulationDescription=description,
                                          simulationStartDateTime=simulation_start ,
                                          simulationStartOffset=-6,
                                          simulationEndDateTime=simulation_end,
                                          simulationEndOffset=-6,
                                          timeStepValue =timestep_value,
                                          timeStepUnitID=timestepunit.UnitsID,
                                          inputDatasetID=dataset.DataSetID)

        return sim

    def createTimeStepUnit(self, timestepabbv, timestepname):
        timestepunit = self.read.getUnits(name = timestepname)
        if not timestepunit:
            u = models.Units()
            u.UnitsTypeCV = 'time'
            u.UnitsAbbreviation = timestepabbv
            u.UnitsName = timestepname
            self.write.createUnit(u)
            timestepunit = self.read.getUnits(name = timestepname)
        return timestepunit[0]

    def createModel(self, modelcode, modeldesc, modelname):
        model = self.read.getModels(codes=modelcode)
        if not model:
            m = models.Models()
            m.ModelCode = modelcode
            m.ModelName = modelname
            m.ModelDescription = modeldesc
            self.write.createModel(m)
            model = self.read.getModels(codes=modelcode)
        return model[0]

    def createMethod(self, organization):


        # method = self.read.getMethods(codes=['simulation'])
        results = self.cursor.execute('SELECT * FROM Methods WHERE MethodCode = ?', ['simulation']).fetchall()

        if not results:
            m = models.Methods()
            m.MethodCode = 'simulation'
            m.MethodName = 'simulation'
            m.MethodTypeCV = 'calculated'
            m.OrganizationID = organization.OrganizationID
            m.MethodDescription = 'Model Simulation Results'
            self.write.createMethod(m)
            results = self.cursor.execute('SELECT * FROM Methods WHERE MethodCode = ?', ['simulation']).fetchone()

        # todo: remove once read.getMethods is fixed
        m = models.Methods()
        m.MethodID = results[0]
        m.MethodTypeCV = results[1]
        m.MethodCode = results[2]
        m.MethodName = results[3]
        m.MethodDescription = results[4]
        m.MethodLink = results[5]
        m.OrganizationID = results[6]

        return m

    def createAffiliation(self, organizationid, personid, user_obj):


        # todo: remove this when the read.getAffiliations code is fixed
        # affiliation = self.read.getAffiliations(personfirst=user_obj.person.first_name, personlast=user_obj.person.last_name, orgcode=user_obj.organization.code)
        results = self.cursor.execute('SELECT * FROM Affiliations WHERE OrganizationID = ? AND PersonID = ?', [organizationid, personid]).fetchall()

        if not results:
            a = models.Affiliations()
            a.PersonID = personid
            a.OrganizationID = organizationid
            a.PrimaryEmail =  user_obj.email
            a.PrimaryPhone = user_obj.phone
            a.PrimaryAddress = user_obj.address
            a.PersonLink = user_obj.personLink
            a.IsPrimaryOrganizationContact = user_obj.isPrimaryOrganizationContact
            a.AffiliationStartDate = user_obj.startDate
            a.AffiliationEndDate = user_obj.affiliationEnd
            self.write.createAffiliation(a)
            results = self.cursor.execute('SELECT * FROM Affiliations WHERE OrganizationID = ? AND PersonID = ?', [organizationid, personid]).fetchall()

        # todo: remove this when the read.getAffiliations code is fixed
        affiliations = []
        for res in results:
            a = models.Affiliations()
            a.PersonID = res[0]
            a.OrganizationID = res[1]
            a.IsPrimaryOrganizationContact = res[2]
            a.AffiliationStartDate = res[3]
            a.AffiliationEndDate = res[4]
            a.PrimaryPhone = res[5]
            a.PrimaryEmail =  res[6]
            a.PrimaryAddress = res[7]
            a.PersonLink = res[8]
            affiliations.append(a)

        return affiliations

    def createOrganization(self, user_obj):

        organization = self.read.getOrganizations(codes = [user_obj.organization.code])
        if not organization:
            o = models.Organizations()
            o.OrganizationTypeCV = user_obj.organization.typeCV
            o.OrganizationCode = user_obj.organization.code
            o.OrganizationName = user_obj.organization.name
            o.OrganizationDescription = user_obj.organization.description
            o.OrganizationLink = user_obj.organization.link
            o.ParentOrganizationID = user_obj.organization.parent
            self.write.createOrganization(o)
            organization = self.read.getOrganizations(codes = [user_obj.organization.code])
        return organization[0]

    def createPerson(self, user_obj):

        person = self.read.getPeople(firstname=user_obj.person.first_name, lastname=user_obj.person.last_name)
        if not person:
            p = models.People()
            p.PersonFirstName = user_obj.person.first_name
            p.PersonMiddleName = user_obj.person.middle_name
            p.PersonLastName = user_obj.person.last_name
            self.write.createPerson(p)
            person = self.read.getPeople(firstname=user_obj.person.first_name, lastname=user_obj.person.last_name)
        return person[0]

    ############ Custom SQL QUERIES ############

    def insert_sampling_feature(self, type='site',code='',name=None,description=None,geometryType=None,elevation=None,elevationDatum=None,WKTgeometry=None):
        '''
        Inserts a sampling feature.  This function was created to support the insertion of Geometry object since this
        functionality is currently lacking from the ODM2PythonAPI.
        :param type: Type of sampling feature.  Must match FeatureTypeCV, e.g. "site"
        :param name: Name of sampling feature (optional)
        :param description: Description of sampling feature (optional)
        :param geometryType: String representation of the geometry type, e.g. Polygon, Point, etc.
        :param elevation: Elevation of the sampling feature (float)
        :param elevationDatum: String representation of the spatial datum used for the elevation
        :param geometry: Geometry of the sampling feature (Shapely Geometry object)
        :return: ID of the sampling feature which was inserted into the database
        '''
        UUID=str(uuid.uuid4())
        FeatureTypeCV=type
        FeatureCode = code
        FeatureName=name
        FeatureDescription=description
        FeatureGeoTypeCV=geometryType
        FeatureGeometry=WKTgeometry
        Elevation=elevation
        ElevationDatumCV=elevationDatum

        # get the last record index
        nextID = self.get_next_insert_id(models.TimeSeriesResultValues)

        values = [nextID,UUID,FeatureTypeCV,FeatureCode,FeatureName,FeatureDescription, FeatureGeoTypeCV, FeatureGeometry, Elevation,ElevationDatumCV]
        self.cursor.execute('INSERT INTO SamplingFeatures VALUES (?, ?, ?, ?, ?, ?, ?, geomFromText(?), ?, ?)'
                            , values)

        # self.conn.commit()

        featureObj = models.SamplingFeatures()
        featureObj.SamplingFeatureID = nextID
        featureObj.SamplingFeatureUUID = UUID
        featureObj.SamplingFeatureTypeCV = FeatureTypeCV
        featureObj.SamplingFeatureCode = FeatureName
        featureObj.SamplingFeatureName = FeatureCode
        featureObj.SamplingFeatureDescription = FeatureDescription
        featureObj.SamplingFeatureGeotypeCV = FeatureGeoTypeCV
        featureObj.Elevation_m = Elevation
        featureObj.ElevationDatumCV = ElevationDatumCV
        featureObj.FeatureGeometry = FeatureGeometry

        return featureObj


    def insert_timeseries_result(self, resultid, aggregationstatistic='Unknown', xloc=None, xloc_unitid=None, yloc=None,yloc_unitid=None, zloc=None, zloc_unitid=None, srsID=None, timespacing=None, timespacing_unitid=None):
        """
        Inserts a timeseries result value
        :param resultid: An ID corresponding to a result record (must exist) (int, not null)
        :param aggregationstatistic:  The time interval over which the recorded value represents an aggregation (varchar, not null)
        :param xloc: XLocation, numeric values and Units can be specified for all three dimensions (float, nullable)
        :param xloc_unitid: The unit id for the xloc (int, nullable)
        :param yloc: YLocation, numeric values and Units can be specified for all three dimensions (float, , nullable)
        :param yloc_unitid: The unit id for the yloc (int, nullable)
        :param zloc: ZLocation, numeric values and Units can be specified for all three dimensions (float, nullable)
        :param zloc_unitid: The unit id for the zloc (int, nullable)
        :param srsID: Spatial reference id for used for the x,y,z locations (int, nullable)
        :param timespacing:  Spacing of the time series values (float, nullable)
        :param timespacing_unitid: Unit of the spacing variable (int, nullable)
        :return: Time series result id
        """

        # insert these data
        values = [resultid, xloc, xloc_unitid, yloc, yloc_unitid, zloc, zloc_unitid, srsID, timespacing, timespacing_unitid, aggregationstatistic]
        self.cursor.execute('INSERT INTO TimeSeriesResults VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
        self.conn.commit()

        # return the id of the inserted record
        return self.cursor.lastrowid

    def insert_timeseries_result_values_bulk(self, ResultIDs = 1, DataValues = [], ValueDateTimes = [],
                                             QualityCodeCV = 'unknown', TimeAggregationIntervalUnitsID = 1,
                                             TimeAggregationInterval = 1, CensorCodeCV = 'nc', ValueDateTimeUTCOffset = -6):
        """
        Performs a bulk insert of time series result values
        :return: True if successful, else False
        ValueID                         (integer)
        ResultID                        (integer)
        DataValue                       (float)
        ValueDateTime                   (datetime)
        ValueDateTimeUTCOffset          (integer)
        CensorCodeCV                    (varchar(255))
        QualityCodeCV                   (varchar(255))
        TimeAggregationInterval         (float)
        TimeAggregationIntervalUnitsID  (integer)
        """
        if ResultIDs == None:
            elog.error('Result ID cannot be None')
            return False

        if len(DataValues) != len(ValueDateTimes):
            elog.error('Length of Values and Dates must be equal')
            return False

        valCount = len(DataValues)

        # convert parameters values into array values
        censor_codes = [CensorCodeCV] * valCount
        quality_codes = [QualityCodeCV] * valCount
        time_unit_ids = [TimeAggregationIntervalUnitsID] * valCount
        time_intervals = [TimeAggregationInterval] * valCount
        time_offsets = [ValueDateTimeUTCOffset] * valCount
        result_ids = [ResultIDs] * valCount

        # convert datetime into apsw accepted format
        value_date_times = [str(d) for d in ValueDateTimes]

        # result_ids = [ResultID] * valCount

        # cannot be none: resultid, timeaggregation interval
        # cannot be empty: datavale, valuedatetime
        # self.spatialDb.execute('INSERT INTO')

        # get the last record index

        nextID = self.get_next_insert_id(models.TimeSeriesResultValues)


        valueIDs = range(nextID, nextID + valCount, 1)


        # vals = [ID, ResultID, DataValue, ValueDateTime, ValueDateTimeUTCOffset, CensorCodeCV, QualityCodeCV, TimeAggregationInterval, TimeAggregationIntervalUnitsID]
        vals = zip(valueIDs, result_ids, DataValues, value_date_times, time_offsets, censor_codes, quality_codes, time_intervals, time_unit_ids)

        # insert values in chunks of 10,000
        sPrint('Begin inserting %d value' % len(vals), MessageType.INFO)

        self.cursor.execute("BEGIN TRANSACTION;")
        chunk_size = 10000
        percent_complete = 0
        for i in range(0, len(vals), chunk_size):
            sidx = i
            eidx = i + chunk_size if (i + chunk_size) < len(vals) else len(vals)
            percent_complete = float(i) / float(len(vals)) * 100
            sPrint('.. inserting records %3.1f %% complete' % (percent_complete), MessageType.INFO)
            self.cursor.executemany('INSERT INTO TimeSeriesResultValues VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', vals[sidx:eidx])
        self.cursor.execute("COMMIT;")

        return 1

    def insert_feature_actions_bulk(self, SamplingFeatureIDs = [], ActionIDs = []):
        """
        Performs a bulk insert of feature action ids
        :return: list of feature action ids
        FeatureActionID                (integer)
        SamplingFeatureID              (integer)
        ActionID                       (integer)
        """

        if len(SamplingFeatureIDs) != len(ActionIDs):
            elog.error('Length SamplingFeatureIDs, and ActionIDs must be equal')
            return False

        valCount = len(SamplingFeatureIDs)

        # get the last record index
        res = self.cursor.execute('SELECT last_insert_rowid() FROM FeatureActions')
        startID = res.fetchone() or (-1,)
        startID = startID[0] + 1 # increment the last id

        FeatureActionIDs = range(startID, startID + valCount, 1)
        vals = zip(FeatureActionIDs, SamplingFeatureIDs, ActionIDs)
        self.cursor.executemany('INSERT OR IGNORE INTO FeatureActions VALUES (?, ?, ?)', vals)


        # return the feature action ids
        return FeatureActionIDs

    def insert_results_bulk(self, FeatureActionIDs=[], ResultTypeCV=None, VariableID=None, UnitsID=None, TaxonomicClassfierID=None,
        ProcessingLevelID=None, ResultDateTime=None, ResultDateTimeUTCOffset=None, ValidDateTime=None, ValidDateTimeUTCOffset=None,
                            StatusCV=None, SampledMediumCV=None, ValueCount=None):
        """
        Performs a bulk insert of results
        :return: list of result ids
        ResultID
        ResultUUID
        FeatureActionID
        ResultTypeCV
        VariableID
        UnitsID
        TaxonomicClassfierID
        ProcessingLevelID
        ResultDateTime
        ResultDateTimeUTCOffset
        ValidDateTime
        ValidDateTimeUTCOffset
        StatusCV
        SampledMediumCV
        ValueCount
        """

        if VariableID is None or UnitsID is None or ProcessingLevelID is None or ValueCount is None \
                        or SampledMediumCV is None or FeatureActionIDs == []:
            elog.error('Failed to bulk insert Results.  VariableID, UnitID, ProcessingLevelID, ValueCount, SampledMediumCV, FeatureActionIDs are required fields.')
            return False

        valCount = len(FeatureActionIDs)

        # get the last record index
        res = self.cursor.execute('SELECT ResultID FROM Results ORDER BY ResultID DESC')
        startID = res.fetchone() or (-1,)
        startID = startID[0] + 1 # increment the last id

        # generate UUIDs for each Result record
        uuids = [uuid.uuid4().hex for i in range(valCount)]
        ResultIDs = range(startID, startID + valCount, 1)

        # convert parameter values into lists
        ResultTypeCV = [ResultTypeCV] * valCount
        VariableID = [VariableID] * valCount
        UnitsID = [UnitsID] * valCount
        TaxonomicClassfierID = [TaxonomicClassfierID] * valCount
        ProcessingLevelID = [ProcessingLevelID] * valCount
        ResultDateTime = [ResultDateTime] * valCount
        ResultDateTimeUTCOffset = [ResultDateTimeUTCOffset] * valCount
        ValidDateTime = [ValidDateTime] * valCount
        ValidDateTimeUTCOffset = [ValidDateTimeUTCOffset] * valCount
        StatusCV = [StatusCV] * valCount
        SampledMediumCV = [SampledMediumCV] * valCount
        ValueCount = [ValueCount] * valCount

        # zip the values up
        vals = zip(ResultIDs, uuids, FeatureActionIDs, ResultTypeCV, VariableID, UnitsID, TaxonomicClassfierID,
                   ProcessingLevelID, ResultDateTime, ResultDateTimeUTCOffset, ValidDateTime, ValidDateTimeUTCOffset,
                   StatusCV, SampledMediumCV, ValueCount)
        self.cursor.executemany('INSERT INTO Results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', vals)


        # return the feature action ids
        return ResultIDs

    def insert_timeseries_results_bulk(self, resultIDs = None, aggregationstatistic='Unknown', xloc=None, xloc_unitid=None, yloc=None, yloc_unitid=None, zloc=None, zloc_unitid=None, srsID=None, timespacing=None, timespacing_unitid=None):
        """
        Performs a bulk insert of timeseries results
        :param resultid: An ID corresponding to a result record (must exist) (int, not null)
        :param aggregationstatistic:  The time interval over which the recorded value represents an aggregation (varchar, not null)
        :param xloc: XLocation, numeric values and Units can be specified for all three dimensions (float, nullable)
        :param xloc_unitid: The unit id for the xloc (int, nullable)
        :param yloc: YLocation, numeric values and Units can be specified for all three dimensions (float, , nullable)
        :param yloc_unitid: The unit id for the yloc (int, nullable)
        :param zloc: ZLocation, numeric values and Units can be specified for all three dimensions (float, nullable)
        :param zloc_unitid: The unit id for the zloc (int, nullable)
        :param srsID: Spatial reference id for used for the x,y,z locations (int, nullable)
        :param timespacing:  Spacing of the time series values (float, nullable)
        :param timespacing_unitid: Unit of the spacing variable (int, nullable)
        :return: Time series result id
        """

        # if VariableID is None or UnitsID is None or ProcessingLevelID is None or ValueCount is None \
        #                 or SampledMediumCV is None or FeatureActionIDs == []:
        #     elog.error('Failed to bulk insert Results.  VariableID, UnitID, ProcessingLevelID, ValueCount, SampledMediumCV, FeatureActionIDs are required fields.')
        #     return False

        valCount = len(resultIDs)

        # # get the last record index
        # res = self.spatialDb.execute('SELECT last_insert_rowid() FROM TimeSeriesResults')
        # startID = res.fetchone() or (-1,)
        # startID = startID[0] + 1 # increment the last id
        #
        # # generate UUIDs for each Result record
        # ResultIDs = range(startID, startID + valCount, 1)

        # convert parameter values into lists
        aggregationstatistic = [aggregationstatistic] * valCount
        xloc = [xloc] * valCount
        xloc_unitid = [xloc_unitid] * valCount
        yloc = [yloc] * valCount
        yloc_unitid = [yloc_unitid] * valCount
        zloc = [zloc] * valCount
        zloc_unitid = [zloc_unitid] * valCount
        srsID = [srsID] * valCount
        timespacing = [timespacing] * valCount
        timespacing_unitid = [timespacing_unitid] * valCount

        # zip the values up
        vals = zip(resultIDs, aggregationstatistic, xloc, xloc_unitid, yloc, yloc_unitid, zloc, zloc_unitid, srsID,
                   timespacing, timespacing_unitid)
        self.cursor.executemany('INSERT INTO TimeSeriesResults VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', vals)


        # return the feature action ids
        return None


    def insert_timeseries_result_values(self, dataframe):
        """
        Inserts timeseries result values using the Pandas library
        :param dataframe: a pandas datatable consisting of all records that will be inserted into the ODM2 database
        :return: true
        """

        # convert pandas table into an insert_many query
        dataframe.to_sql(name='TimeSeriesResultValues', con=self.conn, flavor='sqlite', if_exists='append', index=False)
        self.conn.commit()

        # return true
        return 1

    ###################
    #### GETTERS ######
    ###################

    def getSamplingFeatureID__Geometry_EQUALS(self, wkt_geometry):

        try:
            res = self.cursor.execute('SELECT SamplingFeatureID,'
                                         'SamplingFeatureUUID,'
                                         'SamplingFeatureTypeCV,'
                                         'SamplingFeatureCode,'
                                         'SamplingFeatureName,'
                                         'SamplingFeatureDescription,'
                                         'SamplingFeatureGeotypeCV,'
                                         'Elevation_m,'
                                         'ElevationDatumCV,'
                                         'AsText(FeatureGeometry) '
                                         'FROM SamplingFeatures '
                                         'WHERE Equals ( geomFromText(?) , SamplingFeatures.FeatureGeometry )', [wkt_geometry])

            sf = res.fetchone()
            if sf is None:
                return None

            featureObj = models.SamplingFeatures()
            featureObj.SamplingFeatureID =sf[0]
            featureObj.SamplingFeatureUUID = sf[1]
            featureObj.SamplingFeatureTypeCV = sf[2]
            featureObj.SamplingFeatureCode = sf[3]
            featureObj.SamplingFeatureName = sf[4]
            featureObj.SamplingFeatureDescription = sf[5]
            featureObj.SamplingFeatureGeotypeCV = sf[6]
            featureObj.Elevation_m = sf[7]
            featureObj.ElevationDatumCV = sf[8]
            featureObj.FeatureGeometry = sf[9]

            return featureObj

        except Exception, e:
            sPrint('Encountered and error in getSamplingFeatureId_Geometry_Equals: %s' % e, MessageType.ERROR)
            return None


    def getAllSeries(self):
        """ General select statement for retrieving many results.  This is intended to be used when populating gui tables

        :return :
            :type list:
        """
        try:
            res = self.connection.getSession().query(models.Results). \
                join(models.Variables). \
                join(models.Units). \
                join(models.FeatureActions). \
                join(models.Actions). \
                join(models.TimeSeriesResultValues, models.TimeSeriesResultValues.ResultID == models.Results.ResultID). \
                filter(models.Actions.ActionTypeCV != 'Simulation'). \
                all()
            return res
        except Exception, e:
            sPrint('Encountered and error in getAllSeries: %s' %e, MessageType.ERROR)

    def getAllSimulations(self):
        """
        General select statement for retrieving many simulations.  This is intended to be used for populating gui tables
        :return:
        """
        try:
            res = self.connection.getSession().query(models.Simulations, models.Models, models.Actions, models.People). \
                join(models.Models). \
                join(models.Actions). \
                join(models.ActionBy). \
                join(models.Affiliations). \
                join(models.People).all()
            return res
        except Exception, e:
            sPrint('Encountered an error in get AllSimulations: %s' % e, MessageType.ERROR)

    def getCurrentSession(self):
        return self.connection.getSession()

    ###################
    #### DELETES ######
    ###################

    def deleteSimulation(self, record):
        self.delete.deleteRecord(record.simulation_id)
        if not self.delete.isModelConstraint(record.model_id):
            self.delete.deleteModelByName(record.model_name)


class postgres():

    def __init__(self, session):


        # build sqlalchemy connection
        # self.connection = dbconnection.createConnection('sqlite', sqlitepath)
        self.connection = session
        # sqlitepath = session.engine.url.database

        # create read, write, update, and delete ODM2PythonAPI instances
        self.read = ReadODM2(self.connection)
        self.write = CreateODM2(self.connection)
        self.update = UpdateODM2(self.connection)
        self.delete = DeleteODM2(self.connection)

        # # create connection using spatialite for custom sql queries
        # self.conn = sqlite3.Connection(sqlitepath)
        # self.cursor = self.conn.cursor()
        #
        # # load mod_spatialite extension
        # self.conn.enableloadextension(True)
        # try:
        #     self.cursor.execute('SELECT load_extension("mod_spatialite")')
        # except Exception, e:
        #     elog.error('Encountered and error when attempting to load mod_spatialite: %s' % e)
        #     sPrint('Could not load mod_spatialite.  Your database will not be geo-enabled', MessageType.WARNING)


    def getAllSeries(self):
        """ General select statement for retrieving many results.  This is intended to be used when populating gui tables

        :return :
            :type list:
        """
        res = None
        try:
            res = self.connection.getSession().query(models.Results).\
                join(models.Variables). \
                join(models.Units). \
                join(models.FeatureActions). \
                join(models.Actions). \
                join(models.TimeSeriesResultValues, models.TimeSeriesResultValues.ResultID == models.Results.ResultID).\
                filter(models.Actions.ActionTypeCV != 'Simulation').\
                all()
        except Exception, e:
            print e
            res = None

        return res

    def getAllSimulations(self):
        """
        General select statement for retrieving many simulations.  This is intended to be used for populating gui tables
        :return:
        """
        try:
            res = self.connection.getSession().query(models.Simulations, models.Models, models.Actions, models.People). \
                join(models.Models). \
                join(models.Actions). \
                join(models.ActionBy). \
                join(models.Affiliations). \
                join(models.People).all()
            return res
        except Exception, e:
            sPrint('Encountered an error in get AllSimulations: %s' % e, MessageType.ERROR)