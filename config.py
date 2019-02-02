import os

# possible values: WARN, INFO, DEBUG
LOGGING_LEVEL = 'DEBUG'

# Connection to the database where we save orcid-claims (this database
# serves as a running log of claims and storage of author-related
# information). It is not consumed by others (ie. we 'push' results)
# SQLALCHEMY_URL = 'postgres://docker:docker@localhost:5432/docker'
#SQLALCHEMY_URL = 'postgres://user:password@localhost:15432/augment_pipeline'
#SQLALCHEMY_ECHO = False


# Celery related configuration
# All work we do is concentrated into one exchange (the queues are marked
# by topics, e.g. ads.orcid.claims); The queues will be created automatically
# based on the workers' definition. If 'durable' = True, it means that the 
# queue is created as permanent *AND* the worker will publish 'permanent'
# messages. Ie. if rabbitmq goes down/restarted, the uncomsumed messages will
# still be there 


CELERY_INCLUDE = ['ADSAffil.tasks']
ACKS_LATE=True
PREFETCH_MULTIPLIER=1
CELERYD_TASK_SOFT_TIME_LIMIT = 300


CELERY_DEFAULT_EXCHANGE = 'augment_pipeline'
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"

CELERY_BROKER = 'pyamqp://user:password@localhost:6672/augment_pipeline'
OUTPUT_CELERY_BROKER = 'pyamqp://user:password@localhost:5682/master_pipeline'

OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'


# Affiliation configuration files
AFFDICT_INFILE = '/proj/ads_abstracts/config/affils/Affils_v1.0.0'
PC_INFILE = '/proj/ads_abstracts/config/affils/parent_child.new'
PICKLE_FILE = 'data/aff.pickle'
OUTPUT_FILE = 'output/ml.out'
UNMATCHED_FILE = 'output/unmatched.out'
DIRECT_RECORDS = 'output/direct.json'

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
LM_TEXTLEN = 2048
LM_THRESHOLD = -0.0

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
