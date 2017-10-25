#!/usr/bin/env python

import os

f=open('Affiliations_all_CSG.tsv','r')

affils=dict([])

for l in f.readlines():
    try:
        (code,affstring)=l.strip().split('\t')
    except ValueError:
        print l
        quit()
    else:
        pass
    try:
        affils[code]
    except KeyError:
        affils[code]=[affstring]
    else:
        affils[code].append(affstring)
f.close()

afflist=affils.keys()
affdir=[]

for a in afflist:
    affdir.append(a[0])
affdir=list(set(affdir))

for a in affdir:
    if not os.path.exists(a):
        os.makedirs(a)

for a in afflist:
    filename=str(a[0])+"/"+str(a)
    f=open(filename,'w')
    affs=affils[a]
    for l in affs:
        f.write("%s\t%s\n"%(a,l))
    f.close()
