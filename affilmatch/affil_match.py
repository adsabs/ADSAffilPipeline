#!/usr/bin/env python
#
# amp_beta -- M. Templeton, September 27, 2017
#
# beta testing for the production code
#----------------------------------------------------------------------------

import warnings

import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier

import config

def read_data(lf,colnames):

# Reads in tab-delimited files into pandas data frames.  Note this is
# used for both the input learning model and the data being analyzed, and
# requires that you give it the column names in advance.

    with open(lf,'rU') as f:
        df=pd.read_csv(f,sep='\t',names=colnames,dtype=object)
    f.close()
    return(df)


def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
    return(col_list)



def learning_model(df):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).
#

    alist=column_to_list(df,config.LM_COL_AFFL)

    cv=CountVectorizer(analyzer=config.CV_PARAM_ANALYZER,
                       decode_error=config.CV_PARAM_DECERR)
    ac=cv.fit_transform(alist)
    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)
    clf=SGDClassifier(n_jobs=config.SGDC_PARAM_CPU,
                      random_state=config.SGDC_PARAM_RANDOM,
                      loss=config.SGDC_PARAM_LOSS, 
                      penalty=config.SGDC_PARAM_PENALTY,
                      alpha=config.SGDC_PARAM_ALPHA).fit(cvf,df.index)
    return(cv,tft,clf,alist)



def match_entries(learning_frame,match_frame,cv,tft,clf,colnames):

# This is where the transforms created in learning_model are applied
# to the data being matched, and the best guesses are written to
# match_frame.

    match_namelist=column_to_list(match_frame,config.MATCH_COL_AFFL)

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)


    match_aflist=[]
    match_afscore=[]

    for p,ip in zip(probs,predicted):
        match_aflist.append(learning_frame[config.LM_COL_CODE][ip])
        match_afscore.append(p.max())

    match_frame['Affcodes']=match_aflist
    match_frame['Affscore']=match_afscore

    return(match_frame)
    


def parents_children(infile):
    f=open(infile,'rU')

    children=dict([])
    parents=dict()
    canonical=dict()
    clist=[]

    for l in f.readlines():
        (p,c,mcn,cn)=l.split('\t')
        clist.append(c)
        if len(p) > 0:
            try:
                children[p]
            except KeyError:
                children[p]=[c]
            else:
                children[p].append(c)
            parents[c]=p
        canonical[c]=cn
    f.close()

    return(children,parents,canonical)

def get_parent(affil,parents):
    try:
        parents[affil]
    except KeyError:
        return(affil)
    else:
        return(get_parent(parents[affil],parents))


def print_output(prob_min,match_frame):

    bibcode_string=column_to_list(match_frame,config.MATCH_COL_BIB)
    sequence_string=column_to_list(match_frame,config.MATCH_COL_AISQ)
    test_answers=column_to_list(match_frame,'Affcodes')
    test_scores=match_frame['Affscore'].tolist()

    (children,parents,canonical)=parents_children(config.PC_INFILE)

    matched_affils=open(config.OUTPUT_FILE,'w')

    for ta,bib,seq,ts in zip(test_answers,bibcode_string,sequence_string,test_scores):
        try:
            canonical[ta]
        except KeyError:
            b="ERROR:Bad Key!"
            parent="ERROR:Bad Key!"
        else:
            b=canonical[ta].strip()
            parent=get_parent(ta,parents)
        ts=int(100*ts/prob_min)/100.
        matched_affils.write("%s\t%s\t%s\t%s\t%s\n"%(ta,parent,bib,seq,ts))
    matched_affils.close()

    return



