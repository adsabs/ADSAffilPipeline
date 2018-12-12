
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Table, Column, Integer, Numeric, String, TIMESTAMP,
                        ForeignKey, Boolean, Float)
from sqlalchemy.types import JSON
import json
from adsputils import get_date, UTCDateTime

Base = declarative_base()

from sqlalchemy import types

class CanonicalAffil(Base):
    __tablename__ = 'canon'

    aff_id = Column(String, primary_key=True, unique=True)
    canonical_name = Column(String, nullable=False)
    facet_name = Column(String)
    parents_list = Column(String)
    children_list = Column(String)
    created = Column(UTCDateTime, default=get_date)

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
    created = Column(UTCDateTime, default=get_date)

