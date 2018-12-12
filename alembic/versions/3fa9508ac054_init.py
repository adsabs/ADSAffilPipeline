"""Init
  
Revision ID: 3fa9508ac054
Revises: None
Create Date: 2018-12-12 10:23:29.009126

"""

# revision identifiers, used by Alembic.
revision = '3fa9508ac054'
down_revision = None

from alembic import op
import sqlalchemy as sa

from sqlalchemy import (Table, Column, Integer, Numeric, String, TIMESTAMP,
                        ForeignKey, Boolean, Float)
from sqlalchemy.sql import table, column

import datetime


def upgrade():
    op.create_table('canon',
        Column('aff_id', String, primary_key=True, unique=True),
        Column('canonical_name', String, nullable=False),
        Column('facet_name', String),
        Column('parents_list', String),
        Column('children_list', String),
        Column('created', TIMESTAMP, default=datetime.datetime.utcnow)
    )

    op.create_table('string_ids',
        Column('unique_id', Integer, primary_key=True, unique=True),
        Column('aff_id', String, index=True),
        Column('aff_string', String),
        Column('orig_pub', Boolean),
        Column('orig_ml', Boolean),
        Column('orig_ads', Boolean),
        Column('ml_score', Numeric),
        Column('ml_version', String),
        Column('created', TIMESTAMP, default=datetime.datetime.utcnow)
    )

def downgrade():
    op.drop_table('canon')
    op.drop_table('string_ids')
