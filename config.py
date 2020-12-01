LOGGING_LEVEL = 'debug'

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
SCORE_THRESHOLD = 0.8
