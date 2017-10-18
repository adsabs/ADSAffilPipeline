#!/usr/bin/env python
#
# amp_beta -- M. Templeton, September 27, 2017
#
# beta testing for the production code
#----------------------------------------------------------------------------

import numpy as np
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
#       df=pd.read_csv(f,sep='\t',names=colnames,dtype=str)
        df=pd.read_csv(f,sep='\t',names=colnames)
        f.close()
    print("Done read_data: %s"%lf)
    return(df)



def combine_dictionary(df):

# This function takes the contents of the input dataframe, and merges all
# rows having the same identifier.

    affil_codes=df['Affcode'].unique()
    if len(affil_codes) == len(df):
        print("Skipping combine_dictionary.")
        return df
    else:
        data=[]
        for id in affil_codes:
            mdf=df.loc[df.Affcode==id]
            ltxt=' '.join(mdf.Affil.astype('U',errors='ignore').values.tolist())
            data.append({'Affcode':id,'Affil':ltxt})
        tdf=pd.DataFrame.from_dict(data,dtype=str)
        print("Done combine_dictionary.")
        return(tdf)



def column_to_list(df,colname):
    col_list=df[colname].astype('U',errors='ignore').values.tolist()
    return col_list



def learn_dictionary(df):

# This function creates the framework that sklearn is using to learn the
# characteristics of the text.  The transforms are first created using the
# input data here, and then the resulting models are applied to the data
# to be matched (see match_entries below).
#

    alist=column_to_list(df,'Affil')

    cv=CountVectorizer(analyzer='word', decode_error='replace')
    ac=cv.fit_transform(alist)
    tft=TfidfTransformer()
    cvf=tft.fit_transform(ac)
    clf=SGDClassifier(loss='log', penalty='elasticnet',
                      alpha=1.e-4).fit(cvf,df.index)
    print("Done learn_dictionary.")
    return(cv,tft,clf,alist)



def print_results(df,printcol):

# Takes the resulting data frame of matched and unmatched entries and
# prints them to separate output files.  The unmatched files are output
# in (hopefully) the same format as the input file to facilitate retesting
# and rerunning with different matching criteria.
#
# The matched entries are identical, but have an extra column with a list
# of Affiliation codes from Affiliation_ast_clean.tsv that match the record.
#
    fm=open('aff_matched.txt','w')
    fu=open('aff_unmatched.txt','w')

    bmatch=df.Affcodes.apply(lambda x: len(x)!=0)
    df.loc[bmatch].to_csv(fm,sep='\t',index=False,header=False)
    df.loc[~bmatch].to_csv(fu,sep='\t',index=False,header=False,
                                columns=printcol)
    fm.close()
    fu.close()
    return



def match_entries(dict_frame,match_frame,crit,cv,tft,clf,colnames):

# This is where the transforms created in learn_dictionary are applied
# to the data being matched.
#

    match_namelist=column_to_list(match_frame,'Affil')

    ncv=cv.transform(match_namelist)
    ntf=tft.transform(ncv)
    predicted=clf.predict(ntf)
    probs=clf.predict_proba(ntf)

#!This should be split into two functions, where the code below should
#!be in its own function, like "analyze_stats".  It's more than likely
#!this may be automated separately to do some kind of comparison of
#!different crit values.

    match_aflist=[]
    match_afscore=[]
    match_dict_nwords=[]
    match_dict_nuniq=[]
    match_score_diff=[]
    nids=len(dict_frame)
    minprob=1./float(nids)
    for p,ip in zip(probs,predicted):
        p.sort()
        psig=p.std()
        difcrit=(psig*3.0)
        match_aflist.append(dict_frame.Affcode[ip])
        match_afscore.append(p.max())
        match_dict_nwords.append(len(dict_frame.Affil[ip].split()))
        match_dict_nuniq.append(len(set(dict_frame.Affil[ip].split())))
        match_score_diff.append((p[-1]-p[-10])-difcrit)

    match_frame['Affcodes']=match_aflist
    match_frame['Affscore']=match_afscore
    match_frame['Dnwords']=match_dict_nwords
    match_frame['Dnuniq']=match_dict_nuniq
    match_frame['ScoreD']=match_score_diff
    final_match(match_frame)
    return
    


def final_match(match_frame):

    right_answers=match_frame['GAffcode'].tolist()
    affil_string=match_frame['Affil'].tolist()
    test_answers=match_frame['Affcodes'].tolist()
    test_scores=match_frame['Affscore'].tolist()
    test_nword=match_frame['Dnwords'].tolist()
    test_nuniq=match_frame['Dnuniq'].tolist()
    test_scored=match_frame['ScoreD'].tolist()
    (children,parents,canonical)=parents_children()
    
    og=open('good_test.txt','w')
    ob=open('bad_test.txt','w')
    olg=open('good_test_low.txt','w')
    olb=open('bad_test_low.txt','w')
    for r,a,t,s,x,p,q in zip(right_answers,affil_string,test_answers,test_scores,test_scored,test_nword,test_nuniq):
        guess=check_if_child(t,parents)
        rnew=check_if_child(r,parents)
        if x > -1.:
            if rnew == guess:
                og.write("%s\t%s\t%s\t%s\t%s\t%f\t%f\t%d\t%d\n"%(rnew,guess,a,r,t,s,x,p,q))
            else:
                ob.write("%s\t%s\t%s\t%s\t%s\t%f\t%f\t%d\t%d\n"%(rnew,guess,a,r,t,s,x,p,q))
        else:
            if rnew == guess:
                olg.write("%s\t%s\t%s\t%s\t%s\t%f\t%f\t%d\t%d\n"%(rnew,guess,a,r,t,s,x,p,q))
            else:
                olb.write("%s\t%s\t%s\t%s\t%s\t%f\t%f\t%d\t%d\n"%(rnew,guess,a,r,t,s,x,p,q))
    og.close()
    ob.close()
    olg.close()
    olb.close()

    return



def parents_children():
    infile='ids_canonical_2017Sep15.tsv'
    f=open(infile,'rU')

    children=dict([])
    parents=dict()
    canonical=dict()
    clist=[]

    for l in f.readlines():
        (p,c,cn)=l.split('\t')
        clist.append(c)
        if len(str(p)) > 0:
            try:
                children[str(p)]
            except KeyError:
                children[str(p)]=[str(c)]
            else:
                children[str(p)].append(str(c))
#           try:
#               parents[str(c)]
#           except KeyError:
#               parents[str(c)]=[str(p)]
#           else:
#               parents[str(c)].append(str(p))
            parents[str(c)]=str(p)
        canonical[str(c)]=cn
    f.close()

    return children,parents,canonical

def check_if_child(affil,parents):
    try:
        parents[affil]
    except KeyError:
        return affil
    else:
        return check_if_child(parents[affil],parents)




def get_options():
    import argparse
    parser=argparse.ArgumentParser(description='Affil matching w/sklearn')
    parser.add_argument('infile',type=str,nargs=1,help='file name of input'
                        +' dictionary')
    parser.add_argument('testfile',type=str,nargs=1,help='file name of'
                        +' data to be tested')
    parser.add_argument('crit',type=float,nargs='?',default=30.0,
                        help='threshold crit for positive matching')
    args=parser.parse_args()
    return args.infile[0],args.testfile[0],args.crit



def main():
#   get user inputs for filenames, crit value
    (learn_file,target_file,minsigma)=get_options()

#   read the dictionary data
    affil_frame=read_data(learn_file,['Affcode','Affil'])

#   merge the dictionary data by Affiliation code
    dict_frame=combine_dictionary(affil_frame)

#   get stats on dictionary and put them into a dict
#   keyed to Affcode
#   dict_stats=get_dict_stats(dict_frame)

#   transform dictionary using sklearn
    (cvec,transf,cveclfitr,affil_list)=learn_dictionary(dict_frame)

#   columns in the target data: this is wonky, assumes test file form = const
#   match_columns=['RawAffil','Affil','BibCode']
    match_columns=['GAffcode','Affil']
#   switch Affil and RawAffil around to read the .srcu file with all " deleted
#   match_columns=['Affil','RawAffil','BibCode']

#   read the target data
    match_frame=read_data(target_file,match_columns)

#   classify and output
    match_entries(dict_frame,match_frame,minsigma,cvec,transf,cveclfitr,match_columns)


#   END


if __name__ == '__main__':
    main()
    print("Done!")
