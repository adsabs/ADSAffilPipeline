#!/usr/bin/env python

f=open('matches.txt','rU')

bins=range(9,70)
binc=dict()


for l in f.readlines():
    (ac,ap,bc,rk,score)=l.rstrip().split('\t')
    score=int(10.*float(score))
    try:
        binc[score]
    except KeyError:
        binc[score]=1
    else:
        binc[score]+=1
f.close()

for i in bins:
    try:
        binc[i]
    except KeyError:
        iout=0
    else:
        iout=binc[i]
    print ("%s\t%s"%(i,iout))

