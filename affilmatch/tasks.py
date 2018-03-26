from __future__ import absolute_import, unicode_literals
from kombu import Queue
# todo: create new message for this pipeline to send to master
# from adsmsg import AugmentAffiliation
import os
import config
import affilmatch.app as app_module
from affilmatch.affil_match import *
from adsmsg.augmentrecord import AugmentAffiliationResponseRecord
import pandas as pd


# ============================= INITIALIZATION ==================================== #

proj_home = os.path.realpath(os.path.join(os.path.dirname(__file__), '../'))
app = app_module.ADSAugmentCelery('ads-augment', proj_home=proj_home)
logger = app.logger

logger.info('top of tasks.py, app initialized')

app.conf.CELERY_QUEUES = (
    Queue('affiliation', app.exchange, routing_key='affiliation'),
    Queue('output-results', app.exchange, routing_key='output-results'),
)

warnings.filterwarnings("ignore", category=FutureWarning)

# give thread time to build classifier during initialization
from celery.concurrency import asynpool
asynpool.PROC_ALIVE_TIMEOUT = 100.0

from celery.signals import worker_init

# some global variables to hold scikit objects
#  they are computed in init function and used by worker
learning_frame = None
cvec = None
transf = None
cveclfitr = None
affil_list = None

@worker_init.connect
def init_learning_model(signal, sender, **kw):
    # init learning model for worker
    # build the learning model from various files
    logger.info('ready to read learning_frame')
    global learning_frame, cvec, transf, cveclfitr, affil_list
    learning_frame = read_data(config.LM_INFILE,config.LM_COLS)
    (cvec, transf, cveclfitr, affil_list) = learning_model(learning_frame)
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

    
@app.task(queue='affiliation')
def task_augment_affiliation(message):
    """message should hold bibcode, affiliation number, affiliation string triples
    
    compute response and send it on
    """

    logger.info('in task_augment_affiliation with %s' % message)
    match_frame = pd.DataFrame(to_dataframe(message))
    e = match_entries(learning_frame, match_frame, cvec, transf, cveclfitr, config.MATCH_COLS)

    answers = column_to_list(match_frame,'Affcodes')
    scores = match_frame['Affscore'].tolist()
    logger.info('match returned answers %s and scores %s' % (answers, scores))
    if len(answers) > 0:
        matched = e.to_dict()
        answer_id = matched['Affcodes'][0]
        answer = matched['Affil'][0]
        response = to_response(message, answer, answer_id)
        task_output_results(response)
        logger.info('send affiliation to master %s and %s' % (answer, answer_id))
    else:
        longer.warn('did not find affiliation for bibcode %s with input affiliation string %s',
                    (message.bibcode, message.affiliation))


@app.task(queue='output-results')
def task_output_results(message):
    logger.debug('forward affiliation response to master record: %s', message)
    app.forward_message(message)

def to_dataframe(message):
    """convert request protobuf to scikit dataframe"""
    return pd.DataFrame([{'bibcode': message.bibcode,
                         'Affil': message.affiliation,
                         'Author': message.author,
                         'sequence': message.sequence}])


def to_response(request, answer, answer_id):
    """generate response protobuf to send to master pipeline"""
    d = {'bibcode': request.bibcode,
         'affiliation': request.affiliation,
         'author': request.author,
         'sequence': request.sequence,
         'canonical_affiliation': answer,
         'canonical_affiliation_id': answer_id}
    response = AugmentAffiliationResponseRecord(**d)
    return response
