# affil_match -- M. Templeton
#
# Takes /proj/ads/abstracts/ast/update/AFFILS/Affiliations_all_clean.tsv
# as an input dictionary.  Tries to figure out unresolved references in
# /proj/ads/abstracts/ast/update/AFFILS/affils.ast.20140614_1156.srcu
# Uses a bag-of-words approach with scikit-learn.
#
# Note: as of 2017 July 28, the error rate is too high for this to be useful.
# Tuning of the transforms, etc will probably be required; may also need to
# swap out MultinomialNB for something more sophisticated.
#----------------------------------------------------------------------------

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB


inst_file='Affiliations_all_clean.tsv'
f=open(inst_file,'rU')
affil_frame=pd.read_csv(f,sep='\t',names=['Affcode','Affil'],dtype=str)
f.close()
affil_codes=affil_frame['Affcode'].unique()

tdf=pd.DataFrame(index=[],columns=[])

for id in affil_codes:
#   all_words=[]
    try:
        mdf=affil_frame.loc[affil_frame.Affcode==id]
    except TypeError:
        dummy=0
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
#       all_words=ltxt.split()
#       words=' '.join(list(set(all_words)))
#       tdf=tdf.append(pd.DataFrame(data={'Affcode':id,'Affil':words}
#                                         ,index=[0]),ignore_index=True)
        tdf=tdf.append(pd.DataFrame(data={'Affcode':id,'Affil':ltxt}
                                          ,index=[0]),ignore_index=True)
print("Word-gathering is complete...")


tdf.loc[-1]=['0','asdf']
tdf.index=tdf.index+1
tdf=tdf.sort_index()
affil_list=tdf.Affil.values.astype('U').tolist()
#affil_list=tdf.Affil.values.tolist()

cv=CountVectorizer(analyzer='word',max_df=5.0e-4,decode_error='ignore')
ac=cv.fit_transform(affil_list)

tf_transformer=TfidfTransformer()
cvf=tf_transformer.fit_transform(ac)
clf=MultinomialNB().fit(cvf,tdf.index)
print("Learning model complete...")

infile_target='affils.ast.20170614_1156.srcu'
f=open(infile_target,'rU')
match_frame=pd.read_csv(f,sep='\t',names=['RawAffil','Affil','BibCode'],
                        dtype=str)
match_namelist=match_frame.Affil.values.astype('U').tolist()
#match_namelist=match_frame.Affil.values.tolist()
match_namelist=np.nan_to_num(match_namelist)
print("Loaded target data...")

i_unresolved=len(match_namelist)
match_codelist=[[] for i in range(i_unresolved)]

print("Starting matching...")
while(i_unresolved > 0):
    i_unresolved=0
    new_match_namelist=[]
    ncv=cv.transform(match_namelist)
    ntf=tf_transformer.transform(ncv)
    predicted=clf.predict(ntf)
    for foo,bar,baz in zip(match_namelist,predicted,match_codelist):
        try:
            baz[-1]
        except IndexError:
            dummy=0
        else:
            if(bar == baz[-1]):
                bar=0
        if(bar >0):
            baz.append(bar)
            i_unresolved+=1
            inwords=affil_list[bar].replace(",","").split()
            outwords=foo.replace(",","").split()
            for w in inwords:
                try:
                    outwords.remove(w)
                except ValueError:
                    dummy=0
                finally:
                    dummy=0
            outline=''
            for w in outwords:
                outline+=w+' '
            o2=outline.replace(",","")
            new_match_namelist.append(o2.rstrip())
        else:
            new_match_namelist.append(foo)
    match_namelist=new_match_namelist
    print("Unresolved on this iteration: %s..."%(i_unresolved))

match_aflist=[]
for ac in match_codelist:
    il=[]
    for ic in ac:
        il.append(tdf.Affcode[ic])
    match_aflist.append(il)

match_frame['Affcodes']=match_aflist

bmatch=match_frame.Affcodes.apply(lambda x: len(x)!=0)

print("Done matching.  Writing results...")
fm=open('aff_matched.txt','w')
fu=open('aff_unmatched.txt','w')

match_frame.loc[bmatch].to_csv(fm,sep='\t',index=False,header=False)
match_frame.loc[~bmatch].to_csv(fu,sep='\t',index=False,header=False,
                                columns=['RawAffil','Affil','BibCode'])

fm.close()
fu.close()

print("Done!")
