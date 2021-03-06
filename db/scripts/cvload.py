from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys

# Supporting Python3
try:
    import urllib.request as request
except ImportError:
    import urllib as request
import xml.etree.ElementTree as ET
import argparse



# ################################################################################
# CV  Objects
# ################################################################################
from sqlalchemy import Column,  String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class CVActionType(Base):
    __tablename__ = 'cv_actiontype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CVActionType('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVAggregationStatistic(Base):
    __tablename__ = 'cv_aggregationstatistic'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CVAggregationStatisticsType('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVAnnotationType(Base):
    __tablename__ = 'cv_annotationtype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CVAnnotationType('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVCensorCode(Base):
    __tablename__ = 'cv_censorcode'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CVActionType('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVDatasetType(Base):
    __tablename__ = 'cv_datasettype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVDirectiveType(Base):
    __tablename__ = 'cv_directivetype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVElevationDatum(Base):
    __tablename__ = 'cv_elevationdatum'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVEquipmentType(Base):
    __tablename__ = 'cv_equipmenttype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVMethodType(Base):
    __tablename__ = 'cv_methodtype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVOrganizationType(Base):
    __tablename__ = 'cv_organizationtype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVPropertyDataType(Base):
    __tablename__ = 'cv_propertydatatype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVQualityCode(Base):
     __tablename__ = 'cv_qualitycode'
     # __table_args__ = {u'schema': 'odm2'}

     Term = Column('term', String(255), nullable=False)
     Name = Column('name', String(255), primary_key=True)
     Definition = Column('definition', String(1000))
     Category = Column('category', String(255))
     SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

     def __repr__(self):
         return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVRelationshipType(Base):
    __tablename__ = 'cv_relationshiptype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVResultType(Base):
    __tablename__ = 'cv_resulttype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSampledMedium(Base):
    __tablename__ = 'cv_sampledmedium'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSamplingFeatureGeoType(Base):
    __tablename__ = 'cv_samplingfeaturegeotype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSamplingFeatureType(Base):
    __tablename__ = 'cv_samplingfeaturetype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSpatialOffsetType(Base):
    __tablename__ = 'cv_spatialoffsettype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSpeciation(Base):
    __tablename__ = 'cv_speciation'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSpecimenMedium(Base):
    __tablename__ = 'cv_specimenmedium'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSpecimenType(Base):
    __tablename__ = 'cv_specimentype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))
    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVSiteType(Base):
    __tablename__ = 'cv_sitetype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVReferenceMaterialMedium(Base):
    __tablename__ = 'cv_referencematerialmedium'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVStatus(Base):
    __tablename__ = 'cv_status'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVTaxonomicClassifierType(Base):
    __tablename__ = 'cv_taxonomicclassifiertype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVUnitsType(Base):
    __tablename__ = 'cv_unitstype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVVariableName(Base):
    __tablename__ = 'cv_variablename'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


class CVVariableType(Base):
    __tablename__ = 'cv_variabletype'
    # __table_args__ = {u'schema': 'odm2'}

    Term = Column('term', String(255), nullable=False)
    Name = Column('name', String(255), primary_key=True)
    Definition = Column('definition', String(1000))
    Category = Column('category', String(255))
    SourceVocabularyUri = Column('sourcevocabularyuri', String(255))

    def __repr__(self):
        return "<CV('%s', '%s', '%s', '%s')>" %(self.Term, self.Name, self.Definition, self.Category)


vocab= [
            # ("actiontype", CVActionType),
            # ("qualitycode", CVQualityCode),
            # ("samplingfeaturegeotype", CVSamplingFeatureGeoType),
            # ("elevationdatum", CVElevationDatum),
            # ("resulttype", CVResultType),
            # ("medium", CVSampledMedium),
            # ("speciation", CVSpeciation),
            # ("aggregationstatistic", CVAggregationStatistic),
            # ("methodtype", CVMethodType),
            # ("taxonomicclassifiertype", CVTaxonomicClassifierType),
            # ("sitetype", CVSiteType),
            # ("censorcode", CVCensorCode),
            # ("directivetype", CVDirectiveType),
            # ("datasettype",CVDatasetType),
            # ("organizationtype", CVOrganizationType),
            # ("status", CVStatus),
            # ("annotationtype", CVAnnotationType),
            # ("samplingfeaturetype", CVSamplingFeatureType),
            # ("equipmenttype", CVEquipmentType),
            # ("medium", CVSpecimenMedium),
            # ("spatialoffsettype", CVSpatialOffsetType),
            # ("medium", CVReferenceMaterialMedium),
            # ("specimentype", CVSpecimenType),
            # ("variabletype", CVVariableType),
            # ("variablename", CVVariableName),
            # ("propertydatatype", CVPropertyDataType),
            # ("relationshiptype", CVRelationshipType),
            ("unitstype", CVUnitsType)
            ]



def update_progress(count, value):
    sys.stdout.write("\033[K\r")
    sys.stdout.flush()
    sys.stdout.write("[%-26s] %d%% %s Loaded\r" %
                     ('='*count, (count+0.0)/len(vocab)*100, str(value)))
    sys.stdout.flush()

# ------------------------------------------------------------------------------
#                                   Script Begin
# ------------------------------------------------------------------------------

def load_cv(connection_string):
    """
    Loads controlled vocabulary terms into an empty database
    :param connection_string: connection string, (e.g. mysql+pymysql://ODM:odm@localhost/odm2, postgresql+psycopg2://ODM:odm@test.uwrl.usu.edu/odm2, sqlite:///path/to/my/database.sqlite
    :return: None
    """


    ## Verify connection string
    # conn_string = args.conn_string
    conn_string = connection_string
    engine = None
    session = None
    try:
        engine = create_engine(conn_string, encoding='utf-8')
        session = sessionmaker(bind=engine)()
    except Exception as e:
        print (e)
        sys.exit(0)

    print ("Loading CVs using connection string: %s" % conn_string)

    url = "http://vocabulary.odm2.org/api/v1/%s/?format=skos"

    #XML encodings
    dc = "{http://purl.org/dc/elements/1.1/}%s"
    rdf = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}%s"
    skos = "{http://www.w3.org/2004/02/skos/core#}%s"
    odm2 = "{http://vocabulary.odm2.org/ODM2/ODM2Terms/}%s"


    failed = []
    for count, (key, value) in enumerate(vocab):
        update_progress(count, value)
        try:
            data = request.urlopen(url % key).read()
            root = ET.fromstring(data)
            CVObject = value
            objs = []
            for voc in root.findall(rdf %"Description"):
                try:
                    obj = CVObject()
                    obj.Term = voc.attrib[rdf%"about"].split('/')[-1]

                    if voc.find(skos%"prefLabel") is not None:
                        obj.Name = voc.find(skos%"prefLabel").text
                    else: break
                    if voc.find(skos%"definition") is not None:
                        obj.Definition = voc.find(skos%"definition").text
                    else:
                        # obj.Definition = 'None provided'
                        pass
                        # break
                    obj.Category = category = voc.find(odm2%"category").text if voc.find(odm2 % "category") is not None else None
                    obj.SourceVocabularyUri = voc.attrib[rdf%"about"]
                    # if None not in obj:
                    objs.append(obj)
                except Exception, e:
                    print e
            session.add_all(objs)
            session.commit()
        except Exception as e:
            session.rollback()
            failed.append(key)

    update_progress(len(vocab), "CV_Terms")
    for f in failed:
        sys.stdout.write('Failed to Load CV Terms: %s \n' % f)
    sys.stdout.write("\nCV Load has completed\r\n")
    sys.stdout.flush()



