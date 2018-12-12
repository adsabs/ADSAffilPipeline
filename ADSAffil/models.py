
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, Numeric, String, TIMESTAMP,
                        ForeignKey, Boolean, Float)
from sqlalchemy.types import JSON
import json
from adsputils import get_date

Base = declarative_base()

from sqlalchemy import types
from dateutil.tz import tzutc
from datetime import datetime

class UTCDateTime(types.TypeDecorator):

    impl = TIMESTAMP

    def process_bind_param(self, value, engine):
        if isinstance(value, basestring):
            return get_date(value).astimezone(tzutc())
        elif value is not None:
            return value.astimezone(tzutc()) # will raise Error is not datetime

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=tzutc())

class CanonicalAffil(Base):
    __tablename__ = 'canon'

    aff_id = Column(String, primary_key=True, unique=True)
    canonical_name = Column(String, nullable=False)
    facet_name = Column(String)
    parents_list = Column(String)
    children_list = Column(String)
    created = Column(UTCDateTime, default=datetime.now())

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
    created = Column(UTCDateTime, default=datetime.now())

