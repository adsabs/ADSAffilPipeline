"""
The main application object (it has to be loaded by any worker/script)
in order to initialize the database and get a working configuration.
"""

from __future__ import absolute_import, unicode_literals
from .models import CanonicalAffil, AffStrings
from sqlalchemy.orm import load_only as _load_only
from ADSAffil import utils
from adsputils import ADSCelery, get_date, setup_logging, load_config, u2asc
import json

global adict
try:
    adict = utils.load_affil_dict()
except:
    print "Matching disabled, no matching data available"

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


    def read_canonical_from_db(self):
        dictionary = {}
        with self.session_scope() as session:
            for record in session.query(CanonicalAffil.aff_id,CanonicalAffil.canonical_name,CanonicalAffil.facet_name,CanonicalAffil.parents_list,CanonicalAffil.children_list):
                pj = json.loads(record.parents_list)
                cj = json.loads(record.children_list)
                (p,c) = pj['parents'],cj['children']
                dictionary[record.aff_id] = {'canonical_name':record.canonical_name,'facet_name':record.facet_name,'parents':p,'children':c}
        return dictionary


    def read_affilstrings_from_db(self):
        with self.session_scope() as session:
            dictionary = {}
            for record in session.query(AffStrings.aff_id,AffStrings.aff_string).order_by(AffStrings.aff_id):
                s = record.aff_string
                a = record.aff_id
                if s in dictionary:
                    if dictionary[s] != a:
                        pass
#                       logger.info("Not overwriting existing key pair {0}: {1} with {2}".format(s,dictionary[s],a))
                else:
                    dictionary[s] = a
            return dictionary


    def write_canonical_to_db(self, recs):
        with self.session_scope() as session:
            outrecs = []
            for r in recs:
                outrecs.append(CanonicalAffil(aff_id=r[0],canonical_name=r[1],facet_name=r[2],parents_list=r[3],children_list=r[4]))
            session.bulk_save_objects(outrecs)
            session.commit()


    def write_affilstrings_to_db(self, recs):
        maxlen = 50000
        with self.session_scope() as session:
            while len(recs) > 0:
                outrecs = recs[0:maxlen]
                remainder = recs[maxlen:]
                recs = remainder
                db_outrec = []
                for r in outrecs:
                    try:
                        (affid,affstring)=r.split('\t')
                    except:
                        pass
                    else:
                        db_outrec.append(AffStrings(aff_id=affid,aff_string=affstring,orig_pub=False,orig_ml=False,orig_ads=True,ml_score=0,ml_version=0))
                session.bulk_save_objects(db_outrec)
                session.commit()

