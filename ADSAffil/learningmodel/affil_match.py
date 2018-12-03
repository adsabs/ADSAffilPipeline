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


def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
    return(col_list)



#def learning_model(df):
def learning_model(lmdict):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).
#

    df = pd.DataFrame(lmdict,columns=config.LM_COLS)
    alist=column_to_list(df,config.LM_COL_AFFL)
#   alist = df['Affil'].astype('U', errors='ignore').values.tolist()

    print "learning_model: CountVectorizer"
    cv=CountVectorizer(analyzer=config.CV_PARAM_ANALYZER,
                       decode_error=config.CV_PARAM_DECERR,
                       ngram_range=config.CV_PARAM_NGRAMRANGE)
    print "learning_model: cv.fit_transform"
    ac=cv.fit_transform(alist)
    tft=TfidfTransformer()
    print "learning_model: tft.fit_transform"
    cvf=tft.fit_transform(ac)
    print "learning_model: SGDClassifier + fit"
    clf=SGDClassifier(n_jobs=config.SGDC_PARAM_CPU,
                      random_state=config.SGDC_PARAM_RANDOM,
                      shuffle=True,
                      loss=config.SGDC_PARAM_LOSS,
                      penalty=config.SGDC_PARAM_PENALTY,
                      alpha=config.SGDC_PARAM_ALPHA).fit(cvf,df.index)
    print "learning_model: SGDC sparsify"
    cls=clf.sparsify()
    del clf
    return(cv,tft,cls,alist)



def match_entries(learning_frame,match_frame,cv,tft,clf,colnames):

# This is where the transforms created in learning_model are applied
# to the data being matched, and the best guesses are written to
# match_frame.

    match_namelist=column_to_list(match_frame,colnames)

    print "match_entries: cv.transform"
    ncv=cv.transform(match_namelist)
    print "match_entries: tft.transform"
    ntf=tft.transform(ncv)
    print "match_entries: clf.predict"
    predicted=clf.predict(ntf)
    print "match_entries: clf.predict_proba"
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
        try:
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
        except:
            pass
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

#   bibcode_string=column_to_list(match_frame,config.MATCH_COL_BIB)
#   sequence_string=column_to_list(match_frame,config.MATCH_COL_AISQ)
    test_strings=column_to_list(match_frame,'Affil')
    test_answers=column_to_list(match_frame,'Affcodes')
    test_scores=match_frame['Affscore'].tolist()

    try:
        (children,parents,canonical)=parents_children(config.PC_INFILE)
    except:
        pass

    matched_affils=open(config.OUTPUT_FILE,'w')

#   for ta,bib,seq,ts in zip(test_answers,bibcode_string,sequence_string,test_scores):
    for tt,ta,ts in zip(test_strings,test_answers,test_scores):
        try:
            canonical[ta]
        except KeyError:
            b="ERROR:Bad Key!"
            parent="ERROR:Bad Key!"
        else:
            b=canonical[ta].strip()
            parent=get_parent(ta,parents)
#       ts=int(100*ts/prob_min)/100.
#       ts=ts/prob_min
        ts=int(0.5+(1000.*ts))/1000.
        if ts >= config.LM_THRESHOLD:
            matched_affils.write("%s\t%s\t%s\t%s\n"%(str(ts),b,ta,tt))
    matched_affils.close()

    return


def matcha(matchdict,learningdict):
    error = ""
    print "in matcha.learning_frame"
    learning_frame = pd.DataFrame(learningdict.items(),columns=config.LM_COLS,dtype=object)

    print "in matcha.match_frame"
    match_frame = pd.DataFrame(matchdict,columns=config.MATCH_COLS,dtype=object)

    print "in learning_model"
    (cvec,transf,cveclfitr,affil_list) = learning_model(learning_frame)

#   try:
    print "entering match_entries"
    x = match_entries(learning_frame,match_frame,cvec,transf,cveclfitr,config.MATCH_COLS[0])
#   except:
#       error="Matcha failed in call to match_entries. Stopping."
#   else:
    try:
        print_output((1./len(learning_frame)),x)
    except:
        error="Matcha failed in call to print_output. Stopping."
    return error
