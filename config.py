# Logging: possible levels are DEBUG, INFO, and WARN
LOGGING_LEVEL = 'DEBUG'

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
CELERYD_TASK_SOFT_TIME_LIMIT = 60
CELERY_BROKER = 'pyamqp://'

# Where to send results (of our processing); since we rely on Celery, we have
# to specify the task id - which is the worker's module on the remote side
# that will be handling the message. This is a limitation of the current setup.
# TODO: find a way to send a queue to the remote queue and let Celery deliver
# it to the appropriate worker without having to specify it's name
OUTPUT_CELERY_BROKER = 'pyamqp://guest:guest@localhost:6672/master_pipeline'
OUTPUT_TASKNAME = 'adsmp.tasks.task_update_record'



# Affiliation data files/directories
AFFIL_DATA_DIR = './data/'
TEXT_AFFIL_DICT_FILENAME = AFFIL_DATA_DIR + 'Affils_v3.0.1'
TEXT_PC_DICT_FILENAME = AFFIL_DATA_DIR + 'parent_child.new'
AFFIL_PICKLE_FILENAME = AFFIL_DATA_DIR + 'aff.pickle'
CLAUSE_PICKLE_FILENAME = AFFIL_DATA_DIR + 'clause.pickle'

# Pickling configuration
MAX_PICKLE_PROTOCOL = 4 # 4 works for all Py3, 5 for 3.8+ only

# String matching config
CLAUSE_SEPARATOR = ','
SCORE_THRESHOLD = 0.25
