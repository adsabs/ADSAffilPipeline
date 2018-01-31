#!/usr/bin/env python

import random

f=open('live_affil_test.txt','rU')
inlines=[]
outlines=[]
for l in f.readlines():
    inlines.append(l)

while len(outlines)<50000:
    sr=random.SystemRandom()
    outlines.append(sr.choice(inlines))
f.close()

of=open('test_data','w')
for l in outlines:
    of.write(l)
of.close()
