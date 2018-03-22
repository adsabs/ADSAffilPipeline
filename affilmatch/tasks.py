from __future__ import absolute_import, unicode_literals
from kombu import Queue
# todo: create new message for this pipeline to send to master
# from adsmsg import AugmentAffiliation
import os
import config
import affilmatch.app as app_module
from affilmatch.affil_match import *
import pandas as pd


# ============================= INITIALIZATION ==================================== #

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
app = app_module.ADSAugmentCelery('ads-augment', proj_home=proj_home)
logger = app.logger

logger.info('top of tasks.py, app initialized')

app.conf.CELERY_QUEUES = (
    Queue('augment-affiliation', app.exchange, routing_key='autment-affiliation'),
    Queue('output-results', app.exchange, routing_key='output-results'),
)

warnings.filterwarnings("ignore", category=FutureWarning)

# init learning model for worker
# read the learning model and target data
logger.info('ready to read learning_frame')
learning_frame = read_data(config.LM_INFILE,config.LM_COLS)
logger.info('done reading learning_frame, ready to create learning_model')

import pdb
pdb.set_trace()
(cvec,transf,cveclfitr,affil_list) = learning_model(learning_frame)
logger.info('created learning_model, ready to start worker')

# ============================= TASKS ============================================= #

from celery.signals import worker_process_init

@worker_process_init.connect
def fix_multiprocessing(**_):
  from multiprocessing import current_process
  try:
    current_process()._config
  except AttributeError:
    current_process()._config = {'semprefix': '/mp'}

@app.task(queue='augment_affiliation')
def task_augment_affiliation(message):
    """message should hold bibcode, affiliation number, affiliation string triples"""
    #   classify and output

    logger.info('in task_augment_affiliation with %s' % message)
    # transform learning model using sklearn


    match_frame = pd.DataFrame([{'bibcode': '2017ABCD...17..128D',
                                 'Affil': 'University Delaware',
                                 'Author': 'Doe, Jane',
                                 'sequence': '5/3'}])
    e = match_entries(learning_frame, match_frame, cvec, transf, cveclfitr, config.MATCH_COLS)
    answers=column_to_list(match_frame,'Affcodes')
    scores=match_frame['Affscore'].tolist()
    logger.info('match returned answers %s and scores %s' % (answers, scores))


@app.task(queue='output-results')
def task_output_results(message):
    logger.debug('Will forward this nonbib record: %s', msg)
    app.forward_message(msg)
