#!/usr/bin/env python

PC_INFILE = 'config/parent_child_facet_inst.tsv'
LM_INFILE = 'config/learning_model.dat'

OUTPUT_FILE = 'matches.txt'

LM_COL_CODE = 'Affcode'
LM_COL_AFFL = 'Affil'
LM_COLS = [LM_COL_CODE,LM_COL_AFFL]

MATCH_COL_BIB = 'bibcode'
MATCH_COL_AFFL = 'Affil'
MATCH_COL_AUTH = 'Author'
MATCH_COL_AISQ = 'sequence'
MATCH_COLS = [MATCH_COL_BIB,MATCH_COL_AFFL,MATCH_COL_AUTH,MATCH_COL_AISQ]

CV_PARAM_ANALYZER = 'word'
CV_PARAM_DECERR = 'replace'

SGDC_PARAM_LOSS = 'log'
SGDC_PARAM_PENALTY = 'elasticnet'
SGDC_PARAM_ALPHA = 1.e-4
