#!/usr/bin/env python
#
# amx (affil_match) -- M. Templeton
#
# Takes /proj/ads/abstracts/ast/update/AFFILS/Affiliations_all_clean.tsv
# as an input dictionary.  Tries to figure out unresolved references in
# /proj/ads/abstracts/ast/update/AFFILS/affils.ast.20170614_1156.srcu
# Uses a bag-of-words approach with scikit-learn.
#----------------------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
#from sklearn.linear_model import SGDClassifier




def read_data(lf,colnames):
    try:
        f=open(lf,'rU')
    except IOError:
        print("%s cannot be opened.  Exiting."%(lf))
        quit()
    else:
        df=pd.read_csv(f,sep='\t',names=colnames,dtype=str)
        f.close()
    print("Done read_data: %s\n"%lf)
    return(df)



def combine_dictionary(df):
    tdf=pd.DataFrame(index=[],columns=['Affcode','Affil'])
    for id in affil_codes:
        all_words=[]
        try:
            mdf=affil_frame.loc[affil_frame.Affcode==id]
        except TypeError:
            print("I got a type error for id: %s"%(id))
        else:
            wgl=(mdf.Affil.tolist())
            ltxt=''
            for g in wgl:
                try:
                    ltxt+=' '+g
                except TypeError:
                    dummy=0
                else:
                    dummy=0
            all_words=ltxt.split()
            words=' '.join(list(set(all_words))).replace(",","").strip().rstrip()
            tdf.loc[tdf.shape[0]]=[id,ltxt]  #change ltxt to words if you want
    print("Done combine_dictionary.")
    return(tdf)


def column_to_list(df,colname):
    col_list=df[colname].values.astype('U').tolist()
    return col_list


def learn_dictionary(df):

    alist=column_to_list(df,'Affil')

    cv=CountVectorizer(analyzer='word',decode_error='ignore')
#   cv=CountVectorizer(analyzer='char_wb',ngram_range=(2,6),
#                      decode_error='ignore')

    ac=cv.fit_transform(alist)

    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)

    clf=MultinomialNB().fit(cvf,df.index)
#   clf=SGDClassifier(loss='hinge', penalty='l1',alpha=1e-4,n_iter=1,
#                     random_state=3).fit(cvf,df.index)

    print("Done learn_dictionary.")
    return(cv,tft,clf,alist)



def print_results(df,printcol):
    fm=open('aff_matched.txt','w')
    fu=open('aff_unmatched.txt','w')

    bmatch=df.Affcodes.apply(lambda x: len(x)!=0)
    df.loc[bmatch].to_csv(fm,sep='\t',index=False,header=False)
    df.loc[~bmatch].to_csv(fu,sep='\t',index=False,header=False,
                                columns=printcol)
    fm.close()
    fu.close()
    return



def match_entries(df,crit,cv,tft,clf):
    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)
    pzero=probs.mean()
    pstd=probs.std()
    probs=abs((probs-pzero)/pstd)

    match_aflist=[]
    for p in probs:
        match_aflist.append(dict_frame.Affcode[p>crit].tolist())

    match_frame['Affcodes']=match_aflist
    print("Done matching.  Writing results...")

    print_results(match_frame,['RawAffil','Affil','BibCode'])
    return



# BEGIN MAIN

# user set params -- get via cmd line arguments, move to function.
learn_file='Affiliations_all_clean.tsv'
target_file='affils.ast.20170614_1156.srcu'
minsigma=50.0

affil_frame=read_data(learn_file,['Affcode','Affil'])
affil_codes=affil_frame['Affcode'].unique()
dict_frame=combine_dictionary(affil_frame)
(cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)

match_frame=read_data(target_file,['RawAffil','Affil','BibCode'])

match_namelist=column_to_list(match_frame,'Affil')

print("Loaded target data. Starting matching...")

match_entries(match_namelist,minsigma,cvec,transf,cveclfitr)

print("Done!")
