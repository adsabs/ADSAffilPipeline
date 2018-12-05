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

import ADSAffil.utils as utils
import json

app = app_module.ADSAffilCelery('ads-augment', proj_home=os.path.realpath(os.path.join(os.path.dirname(__file__), '../')))

app.conf.CELERY_QUEUES = (
#   Queue('load-affstrings', app.exchange, routing_key='load-affstrings'),
#   Queue('load-canonical', app.exchange, routing_key='load-canonical'),
#   Queue('read-affstrings', app.exchange, routing_key='read-affstrings'),
#   Queue('read-canonical', app.exchange, routing_key='read-canonical'),
#   Queue('match-affils', app.exchange, routing_key='match-affils'),
#   Queue('resolve-unmatched', app.exchange, routing_key='resolve-unmatched'),
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

# Canonical parent-child facet info
# Reading and populating the db of affiliation IDs, canonical and facet strings, and parent-child info

#@app.task(queue='load-canonical')
def task_db_canonical_id_list(recs):
    if len(recs) > 0:
        outrecs=[]
        for r in recs:
            outrecs.append(CanonicalAffil(aff_id=r[0],canonical_name=r[1],facet_name=r[2],parents_list=r[3],children_list=r[4]))
        session.bulk_save_objects(outrecs)
        session.commit()



#@app.task(queue='load-affstrings')
def task_db_affil_string_dict(recs):
    if len(recs) > 0:
        outrecs = []
        for r in recs:
            outrecs.append(AffStrings(aff_id=r[0],aff_string=r[1],orig_pub=r[2],orig_ml=r[3],orig_ads=r[4],ml_score=r[5],ml_version=r[6]))
        session.bulk_save_objects(outrecs)
        session.commit()


#@app.task(queue='read-affstrings')
def task_db_readall_affstrings():
    dictionary = {}
    for record in session.query(AffStrings.aff_id,AffStrings.aff_string).order_by(AffStrings.aff_id):
        s = record.aff_string
        a = record.aff_id
        if s in dictionary:
            if dictionary[s] != a:
                logger.info("Not overwriting existing key pair {0}: {1} with {2}".format(s,dictionary[s],a))
        else:
            dictionary[s] = a
    return dictionary



#@app.task(queue='read-canonical')
def task_db_readall_canonical():
    dictionary = {}
    try:
        for record in session.query(CanonicalAffil.aff_id,CanonicalAffil.canonical_name,CanonicalAffil.facet_name,CanonicalAffil.parents_list,CanonicalAffil.children_list):
            (p,c) = record.parents_list['parents'],record.children_list['children']
            dictionary[record.aff_id] = {'canonical_name':record.canonical_name,'facet_name':record.facet_name,'parents':p,'children':c}
    except:
        logger.warn("Warning: failed to read from CanonicalAffil.")
    return dictionary


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
