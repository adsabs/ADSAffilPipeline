"""
The main application object (it has to be loaded by any worker/script)
in order to initialize the database and get a working configuration.
"""

from __future__ import absolute_import, unicode_literals
from .models import CanonicalAffil, AffStrings
from ADSAffil import utils
from adsputils import ADSCelery, get_date, setup_logging, load_config, u2asc
import json

#global adict
#try:
#    adict = utils.load_affil_dict(config.PICKLE_FILE)
#except:
#    print "Matching disabled, no matching data available"

def augmenter(afstring):
#   logging.captureWarnings(True)
    m_id = utils.affil_id_match(afstring,adict)
    try:
        facet = cdict[m_id]['facet_name']
        abbrev = facet
        pids = cdict[m_id]['parents']
        canon = cdict[m_id]['canonical_name']
    except:
        return (u"-",u"-",None)
    else:
        afh = []
        if pids[0] == u"-":
            fbase = u"0/"+facet
            fchild = u"1/"+facet+u"/"+facet
            afh.append(fbase)
            afh.append(fchild)
        else:
            for x in pids:
                fp = cdict[x]['facet_name']
                fbase = u"0/"+fp
                fchild = u"1/"+fp+u"/"+facet
                afh.append(fbase)
                afh.append(fchild)
        return (abbrev,canon,afh)


class ADSAffilCelery(ADSCelery):
    def augment_affiliations(self, rec):
        global cdict
        cdict = self.read_canonical_from_db()
        bibc = rec["bibcode"]
        aff = rec["aff"]
        id_list = []
        can_list = []
        aff_facet_hier = []
        facet = []
        unmatched = {}
        for s in aff:
            s = utils.reencode_string(utils.back_convert_entities(s)[0])
            if ';' in s:
                t = s.split(';')
                idl = []
                cl = []
                for v in t:
                    if v.strip() != '':
                        v = utils.reencode_string(utils.back_convert_entities(v)[0])
                        (aid,can,fac) = augmenter(v)
                        idl.append(aid)
                        cl.append(can)
                        if fac:
                            facet.append(fac)
                        else:
                            if v != u"" and v !=u"-":
                                unmatched[v] = u"0"
                if not isinstance(cl,basestring):
                    cl = u'; '.join(cl)
                id_list.append(u'; '.join(idl))
                can_list.append(cl)
            else:
                (aid,can,fac) = augmenter(s)
                id_list.append(aid)
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
        rec["aff_canonical"] = can_list
        rec["aff_facet_hier"] = aff_facet_hier
        return unmatched
