from __future__ import absolute_import, unicode_literals
from kombu import Queue
import os
import config

import pandas as pd

from ADSAffil import app as app_module
from ADSAffil.curate import parent_child_facet as pcf
from ADSAffil.curate import affil_strings as af
from ADSAffil.models import *
from ADSAffil.learningmodel import affil_match as lm
from ADSAffil.learningmodel import make_learner as mkl
#from adsmsg import BibRecord, DenormalizedRecord
from adsmsg import AugmentAffiliationResponseRecord

import ADSAffil.utils as utils
import json

app = app_module.ADSAffilCelery('augment-pipeline', proj_home=os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation'),
    Queue('output-record', app.exchange, routing_key='output-record'),
    Queue('read-affildata', app.exchange, routing_key='read-affildata'),
    Queue('write-affildata', app.exchange, routing_key='write-affildata')
)
logger = app.logger


@app.task(queue='augment-affiliation')
def task_augment_affiliations(rec):
#   try:
        u = app.augment_affiliations(rec)
        unmatched.update(u)
        task_output_augmented_record.delay(rec)
#   except:
#       logger.error("Error augmenting record: %s", rec['bibcode'])
#       raise BaseException("Error augmenting record %s:"%rec['bibcode'])


@app.task(queue='output-record')
def task_output_augmented_record(rec):
    logger.debug('Will forward this record: %s', rec)

    msg = AugmentAffiliationResponseRecord(rec)
    app.forward_message(msg)


@app.task(queue='write-affildata')
def task_write_canonical_to_db(recs):
    if len(recs) > 0:
        try:
            app.write_canonical_to_db(recs)
        except:
            raise BaseException("Could not write canonical to db")


@app.task(queue='write-affildata')
def task_write_affilstrings_to_db(recs):
    if len(recs) > 0:
        try:
            app.write_affilstrings_to_db(recs)
        except:
            raise BaseException("Could not write affilstrings to db")


@app.task(queue='read-affildata')
def task_read_canonical_from_db():
    try:
        dictionary = app.read_canonical_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


@app.task(queue='read-affildata')
def task_read_affilstrings_from_db():
    try:
        dictionary = app.read_affilstrings_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


def task_make_learning_model(aff_dict):
    learningmodel = mkl.make_learner(aff_dict)
    return learningmodel


def task_resolve_unmatched(stringdict,learningdict):
    try:
        e = lm.matcha(stringdict,learningdict)
    except:
        logger.error("Machine learning matching failed.  Stopping")
    else:
        if e != "":
            logger.error("Machine learning matching failed.  No output.")


def task_output_unmatched(unmatched_strings):
    try:
        if len(unmatched_strings) > 0:
            with open(config.UNMATCHED_FILE,'a') as fo:
                for l in unmatched_strings:
                    fo.write(l+"\n")
    except:
        logger.error("Failed to write unmatched strings to file.  No output.")
