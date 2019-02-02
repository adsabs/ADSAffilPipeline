"""
The main application object (it has to be loaded by any worker/script)
in order to initialize the database and get a working configuration.
"""

from __future__ import absolute_import, unicode_literals
from ADSAffil import utils
from adsputils import ADSCelery, get_date, setup_logging, load_config, u2asc
import json
import config

global adict,cdict
try:
    (adict,cdict) = utils.read_pickle(config.PICKLE_FILE)
except:
    print "No pickle file, unable to do direct matching.\nYou should only ever see this if you're creating a pickle\nfile for the first time with 'run.py -lf -mp'"


def augmenter(afstring):
    m_id = utils.affil_id_match(afstring,adict)
    print "LOLOLOL: %s"%m_id
    try:
        facet = cdict[m_id]['facet_name']
        pids = cdict[m_id]['parents']
        canon = cdict[m_id]['canonical_name']
    except:
        return (u"-",u"-",None)
    else:
        afh = []
        if pids[0] == u"-":
            fbase = u"0/"+facet
            fchild = u"1/"+facet+u"/"+facet
            abbrev = facet+u"/"+facet
            afh.append(fbase)
            afh.append(fchild)
        else:
            abbrev_list = []
            for x in pids:
                fp = cdict[x]['facet_name']
                fbase = u"0/"+fp
                fchild = u"1/"+fp+u"/"+facet
                abbrev = fp+u"/"+facet
                abbrev_list.append(abbrev)
                afh.append(fbase)
                afh.append(fchild)
            abbrev = "; ".join(abbrev_list)
        return (abbrev,canon,afh,m_id)


class ADSAffilCelery(ADSCelery):
#   def __init__(self):
#       self.adict = {}

    def augment_affiliations(self, rec):
        bibc = rec["bibcode"]
        aff = rec["aff"]
        id_list = []
        idc_list = []
        can_list = []
        aff_facet_hier = []
        facet = []
        unmatched = {}
        for s in aff:
            s = utils.reencode_string(utils.back_convert_entities(s)[0])
            if ';' in s:
                t = s.split(';')
                idl = []
                idcl = []
                cl = []
                for v in t:
                    if v.strip() != '':
                        v = utils.reencode_string(utils.back_convert_entities(v)[0])
                        (aid,can,fac,idcode) = augmenter(v)
                        idl.append(aid)
                        idcl.append(idcode)
                        cl.append(can)
                        if fac:
                            facet.append(fac)
                        else:
                            if v != u"" and v !=u"-":
                                unmatched[v] = u"0"
                if not isinstance(cl,basestring):
                    cl = u'; '.join(cl)
                id_list.append(u'; '.join(idl))
                idc_list.append(u'; '.join(idcl))
                can_list.append(cl)
            else:
                (aid,can,fac,idcode) = augmenter(s)
                id_list.append(aid)
                idc_list.append(idcode)
                can_list.append(can)
                if fac:
                    facet.append(fac)
                else:
                    if s != u"" and s !=u"-":
                        unmatched[s] = u"0"
    
        if len(facet) > 0:
            f2 = []
            for f in facet:
                if len(f) == 1:
                    f2.append(f[0])
                else:
                    for x in f:
                        f2.append(x)
            try:
                f4 = []
                for f3 in list(set(f2)):
                    if isinstance(f3,list):
                        for x in list(f3):
                            f4.append(x)
                    else:
                        f4.append(f3)
                f2 = f4
            except:
                pass
            aff_facet_hier = f2
        else:
            aff_facet_hier = []
    
#       rec["aff_abbrev"] = aff_facet_hier
        rec["aff_abbrev"] = id_list
        rec["aff_id"] = idc_list
        rec["aff_canonical"] = can_list
        rec["aff_facet_hier"] = aff_facet_hier
        return unmatched
