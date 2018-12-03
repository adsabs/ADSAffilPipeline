from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import (Table, Column, Integer, Numeric, String, TIMESTAMP,
                        ForeignKey, Boolean, Float)
          
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB,ENUM

USERNAME = 'matthewt'
PASSWORD = 'Plenary3Ester9Golly2'

engine = create_engine('postgres://'+USERNAME+':'+PASSWORD+'@localhost:' \
                       '5432/matthewt')

Session = sessionmaker(bind=engine)

session = Session()

Base = declarative_base()

from sqlalchemy import types
from dateutil.tz import tzutc
from datetime import datetime

#class augmented_affil_data(Base):
#    __tablename__ = 'affiliation_id'
#    enum_col_1 = ENUM('ads','user','pub','match',name='id_origin', create_type=False)
#
#    unique_id = Column(Integer, primary_key=True, unique=True)
#    bibcode = Column(String(19), index=True)
##   affil_id = Column(JSONB, server_default="'{}'")
#    affil_id = Column(String)
#    iauth = Column(Integer)
#    iaffil = Column(Integer)
#    origin = Column(enum_col_1)
#    created = Column(TIMESTAMP, default=datetime.now())
#
#    def __repr__(self):
#        return "affiliation_id(bibcode='{self.bibcode}', affil_id='{self.affil_id}')".format(self=self)
#
#
class CanonicalAffil(Base):
    __tablename__ = 'canon'

    aff_id = Column(String, primary_key=True, unique=True)
    canonical_name = Column(String, nullable=False)
    facet_name = Column(String)
    parents_list = Column(JSONB, server_default="'{}'")
    children_list = Column(JSONB, server_default="'{}'")
    created = Column(TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return "CanonicalAffil(aff_id='{self.aff_id}')".format(self=self)

class AffStrings(Base):
    __tablename__ = 'string_ids'

    unique_id = Column(Integer, primary_key=True, unique=True)
    aff_id = Column(String, index=True)
    aff_string = Column(String)
    orig_pub = Column(Boolean)
    orig_ml = Column(Boolean)
    orig_ads = Column(Boolean)
    ml_score = Column(Numeric)
    ml_version = Column(String)
    created = Column(TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return "AffStrings(aff_id='{self.aff_id}')".format(self=self)
    
#class affil_string_match(Base):
#    __tablename__ = 'affil_string_dictionary'
#    enum_col_2 = ENUM('ads','user','lm',name='aff_origin', create_type=False)
#
#    unique_id = Column(Integer, primary_key=True, unique=True)
#    aff_id = Column(String, index=True)
#    aff_string = Column(String)
#    origin = Column(enum_col_2)
#    created = Column(TIMESTAMP, default=datetime.now())
#
#    def __repr__(self):
#        return "affil_string_dictionary(aff_id='{self.aff_id}')".format(self=self)
