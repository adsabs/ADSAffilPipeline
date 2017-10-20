#!/usr/bin/env python
#
# amp_beta -- M. Templeton, September 27, 2017
#
# beta testing for the production code
#----------------------------------------------------------------------------
import warnings

from config.config import *
import warnings
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier



def read_data(lf,colnames):

# Reads in tab-delimited files into pandas data frames.  Note this is
# used for both the input dictionary and the data being analyzed, and
# requires that you give it the column names in advance.

    try:
        f=open(lf,'rU')
    except IOError:
        print("%s cannot be opened.  Exiting."%(lf))
        quit()
    else:
        df=pd.read_csv(f,sep='\t',names=colnames)
        f.close()
    return(df)



def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
    return col_list



def learn_dictionary(df):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).
#

    alist=column_to_list(df,DICT_COL_AFFL)

    cv=CountVectorizer(analyzer=CV_PARAM_ANALYZER,
                       decode_error=CV_PARAM_DECERR)
    ac=cv.fit_transform(alist)
    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)
<<<<<<< HEAD
    clf=SGDClassifier(loss=SGDC_PARAM_LOSS, penalty=SGDC_PARAM_PENALTY,
                      alpha=SGDC_PARAM_ALPHA).fit(cvf,df.index)
=======
    clf=SGDClassifier(loss='log', penalty='elasticnet',
                      alpha=1.e-4).fit(cvf,df.index)
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
    return(cv,tft,clf,alist)



def match_entries(dict_frame,match_frame,cv,tft,clf,colnames):

# This is where the transforms created in learn_dictionary are applied
# to the data being matched, and the best guesses are written to
# match_frame.

    match_namelist=column_to_list(match_frame,MATCH_COL_AFFL)

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)


    match_aflist=[]
    match_afscore=[]

    for p,ip in zip(probs,predicted):
<<<<<<< HEAD
#       match_aflist.append(dict_frame.Affcode[ip])
        match_aflist.append(dict_frame[DICT_COL_CODE][ip])
=======
        match_aflist.append(dict_frame.Affcode[ip])
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
        match_afscore.append(p.max())

    match_frame['Affcodes']=match_aflist
    match_frame['Affscore']=match_afscore

    return match_frame
    


<<<<<<< HEAD
def parents_children(infile):
=======
def parents_children():
    infile='config/MT_2017Oct16_parent_child_facet_inst.tsv'
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
    f=open(infile,encoding='ascii',errors='replace')

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

    return children,parents,canonical

def get_parent(affil,parents):
    try:
        parents[affil]
    except KeyError:
        return affil
    else:
        return get_parent(parents[affil],parents)


def print_output(prob_min,match_frame):
<<<<<<< HEAD
    bibcode_string=column_to_list(match_frame,MATCH_COL_BIB)
    sequence_string=column_to_list(match_frame,MATCH_COL_AISQ)
    test_answers=column_to_list(match_frame,'Affcodes')
    test_scores=match_frame['Affscore'].tolist()
    matched_affils=open(OUTPUT_FILE,'w')
    (children,parents,canonical)=parents_children(PC_INFILE)
=======
    bibcode_string=column_to_list(match_frame,'bibcode')
    sequence_string=column_to_list(match_frame,'sequence')
    test_answers=column_to_list(match_frame,'Affcodes')
    test_scores=match_frame['Affscore'].tolist()
    matched_affils=open('matched.txt','w')
    unmatched_affils=open('unmatched.txt','w')
    (children,parents,canonical)=parents_children()
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
    for ta,bib,seq,ts in zip(test_answers,bibcode_string,sequence_string,test_scores):
        try:
            canonical[ta]
        except KeyError:
            b="ERROR:Bad Key!"
            parent="ERROR:Bad Key!"
        else:
            b=canonical[ta].strip()
<<<<<<< HEAD
            parent=get_parent(ta,parents)
        ts=int(100*ts/prob_min)/100.
        matched_affils.write("%s\t%s\t%s\t%s\t%s\n"%(ta,parent,bib,seq,ts))
    matched_affils.close()
=======
            parent=parents_children(ta)
        if (ts >= 2.*prob_min):
            matched_affils.write("%s\t%s\t%s\t%s\t%s\t%f16.10\n"%(ta,parent,b,bib,seq,ts))
        else:
            unmatched_affils.write("%s\t%s\t%s\t%s\t%s\t%f16.10\n"%(ta,parent,b,bib,seq,ts))
    matched_affils.close()
    unmatched_affils.close()
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
    return



def get_options():
    import argparse
    parser=argparse.ArgumentParser(description='Affil matching w/sklearn')
    parser.add_argument('testfile',type=str,nargs=1,help='file name of'
                        +' data to be tested')
    args=parser.parse_args()
    return args.testfile[0]



def main():
<<<<<<< HEAD

=======
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558
#   because sklearn is throwing an annoying FutureWarning in python3
    warnings.filterwarnings("ignore", category=FutureWarning)

#   get user inputs for filenames
    target_file=get_options()

#   read the dictionary data
<<<<<<< HEAD
    dict_frame=read_data(DICT_INFILE,DICT_COLS)
=======
    dict_frame=read_data('config/dictionary.dat',['Affcode','Affil'])
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558

#   transform dictionary using sklearn
    (cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)


#   read the target data
    match_frame=read_data(target_file,MATCH_COLS)

#   classify and output
    print_output((1./len(dict_frame)),match_entries(dict_frame,match_frame,cvec,transf,cveclfitr,MATCH_COLS))

<<<<<<< HEAD

=======
>>>>>>> 220caadf1d1bdda8755d1de658153f3db9a41558

if __name__ == '__main__':
    main()
