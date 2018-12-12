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
from adsmsg import BibRecord, DenormalizedRecord

import ADSAffil.utils as utils
import json

app = app_module.ADSAffilCelery('augment-pipeline', proj_home=os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

app.conf.CELERY_QUEUES = (
    Queue('read-affdata', app.exchange, routing_key='read-affdata'),
    Queue('write-affdata', app.exchange, routing_key='write-affdata'),
    Queue('augment-affiliation', app.exchange, routing_key='augment-affiliation')
)
logger = app.logger


@app.task(queue='augment-affiliation')
def task_augment_affiliations(rec):
    try:
        unmatched = app.augment_affiliations(rec)
    except:
        raise BaseException("Error augmenting record %s:"%rec['bibcode'])
    else:
        return unmatched

@app.task(queue='write-affdata')
def task_write_canonical_to_db(recs):
    if len(recs) > 0:
#       try:
        app.write_canonical_to_db(recs)
#       except:
#           raise BaseException("Could not write canonical to db")

@app.task(queue='write-affdata')
def task_write_affilstrings_to_db(recs):
    if len(recs) > 0:
        try:
            app.write_affilstrings_to_db(recs)
        except:
            raise BaseException("Could not write affilstrings to db")


@app.task(queue='read-affdata')
def task_read_canonical_from_db():
    try:
        dictionary = app.read_canonical_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


@app.task(queue='read-affdata')
def task_read_affilstrings_from_db():
    try:
        dictionary = app.read_affilstrings_from_db()
    except:
        raise BaseException("Could not read canonical from db")
    else:
        return dictionary


# Non-app tasks: move somewhere else (utils or app?)
#@app.task(queue='read-affstrings')
def task_make_learning_model(aff_dict):
    learningmodel = mkl.make_learner(aff_dict)
    return learningmodel


#@app.task(queue='resolve-unmatched')
def task_resolve_unmatched(stringdict,learningdict):
    try:
        e = lm.matcha(stringdict,learningdict)
    except:
        logger.error("Machine learning matching failed.  Stopping")
    else:
        if e != "":
            logger.error("Machine learning matching failed.  No output.")


#@app.task(queue='resolve-unmatched')
def task_output_unmatched(unmatched_strings):
    try:
        if len(unmatched_strings) > 0:
            with open(config.UNMATCHED_FILE,'a') as fo:
                for l in unmatched_strings:
                    fo.write(l+"\n")
    except:
        logger.error("Failed to write unmatched strings to file.  No output.")
