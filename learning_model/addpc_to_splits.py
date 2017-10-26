#!/usr/bin/env python
import glob
from math import sqrt

def file_len(fname):
    with open(fname) as f:
        i=-1
        for i, l in enumerate(f):
            pass
    return i + 1

pcfile=open('pc_facet_ascii.tsv','rU')
saff=dict()
laff=dict()
for l in pcfile.readlines():
  (parent,child,shorta,longa)=l.split('\t')
  saff[child]=shorta
  laff[child]=longa

files=glob.glob("[A123456789]/*")

for f in files:
    nlines=file_len(f)
    if(nlines >2):
        nlines=10+int(sqrt(nlines))
    else:
        nlines=10

    (dname,aff)=f.split('/')
    try:
        saff[aff]
    except KeyError:
        pass
    else:
        xf=open(f,'a')
        lo=aff+'\t'+saff[aff]+' '+laff[aff]
        xf.write(lo*nlines)
        
