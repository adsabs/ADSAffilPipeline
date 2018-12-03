#!/usr/bin/env python

#ADD Documentation to make it clear what these variables are!

# used by ADSPiplelineUtils to connect
ACKS_LATE=True
PREFETCH_MULTIPLIER=1
CELERY_BROKER = 'pyamqp://guest@localhost:5682/augment_pipeline'
CELERY_DEFAULT_EXCHANGE = 'ads-augment'
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
OUTPUT_CELERY_BROKER = 'pyamqp://guest:guest@localhost:5682/master_pipeline'
OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'

# Affiliation configuration files
PC_INFILE = '/Users/mtempleton/Projects/Github_repos/dev/Affil_New/data/parent_child.new'
AFFDICT_INFILE = '/Users/mtempleton/Projects/Github_repos/dev/Affil_New/data/Affiliations_all.new'
PICKLE_FILE = '/Users/mtempleton/Projects/Github_repos/dev/Affil_New/data/aff.pickle'
OUTPUT_FILE = 'ml.out'
UNMATCHED_FILE = 'unmatched.out'
DIRECT_RECORDS = 'direct.json'

# These are column headings used in the learning model file.  These are used
# in the case where the structure of a learning model file may be different,
# than a simple two column format with 'Affcode' and 'Affil' in that order.
# In that case, the input file should have a column with the same name as
# LM_COL_CODE, LM_COL_AFFL, and an array that defines where those columns
# are relative to the whole document (e.g. ['foo','bar',LM_COL_AFFL,'baz',
# 'LM_COL_CODE','lol']
# LM_TEXTLEN is the maximum length that strings in the learning model can
# have.  It's needed to keep the model from running out of memory (which
# can easily happen.)
LM_COL_CODE = 'Affcode'
LM_COL_AFFL = 'Affil'
LM_COLS = [LM_COL_CODE,LM_COL_AFFL]
LM_TEXTLEN = 4096
LM_THRESHOLD = +0.8

MATCH_COL_AFFL = 'Affil'
MATCH_COLS = [MATCH_COL_AFFL]

CV_PARAM_ANALYZER = 'word'
CV_PARAM_DECERR = 'replace'
CV_PARAM_NGRAMRANGE = (1,4)

SGDC_PARAM_LOSS = 'log'
SGDC_PARAM_PENALTY = 'elasticnet'
SGDC_PARAM_ALPHA = 7.e-8
#SGDC_PARAM_RANDOM = None
SGDC_PARAM_RANDOM = 12345
#SGDC_PARAM_CPU = 4
#SGDC_PARAM_CPU = 1
SGDC_PARAM_CPU=-1
