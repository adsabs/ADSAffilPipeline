with open("ml.out","rU") as fp:
    gdict = {}
    for l in fp.readlines():
        (score,guess,cid,instring)=l.strip().rstrip().split('\t')
        if cid in gdict:
            gdict[cid.strip()].append(l.strip().rstrip())
        else:
            gdict[cid.strip()] = [l.strip().rstrip()]



kl = sorted(gdict.keys())
for k in kl:
    la = gdict[k]
#   ls = sorted(la, key = lambda x: x.split[0])
    ls = sorted(la, reverse = True)
    for l in ls:
        print l.strip()
    print
