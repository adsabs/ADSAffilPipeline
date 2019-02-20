"""
The main application object (it has to be loaded by any 
worker/script) in order to initialize the workers
"""

from __future__ import absolute_import, unicode_literals
from ADSAffil import utils
from adsputils import ADSCelery, get_date, setup_logging, load_config, u2asc
import json


class FatalException(Exception):
    pass

def augmenter(afstring, adict, cdict):
    """
    Where string matching happens: if a given string (afstring)
    is present in adict, m_id will be the affiliation id
    assigned to that string.  If it isn't present, m_id will
    be "0" (which has no entry in cdict).

    The aff_abbrev and aff_facet_hier fields for each afstring
    are being filled here, in addition to finding the canonical
    values.  If the m_id doesn't have a parent (pids[0]=='-'), then
    the facet heirarchy is "0/affil, 1/affil/affil".  Otherwise
    it's "0/parent, 1/parent/affil"; since an affil can have
    multiple parents (e.g. Harvard and SI for CfA), you need to
    treat them as lists.
    """
    m_id = utils.affil_id_match(afstring, adict)
    try:
        facet = cdict[m_id]['facet_name']
        pids = cdict[m_id]['parents']
        canon = cdict[m_id]['canonical_name']
    except:
        # Not found in cdict -- can't ID affil string
        return (u'-', u'-', None, u'-')
    aff_facet_hier = []
    if pids[0] == u'-':
        # No parents...
        fbase = u'0/' + facet
        fchild = u'1/' + facet + u'/' + facet
        abbrev = facet + u'/' + facet
        aff_facet_hier.append(fbase)
        aff_facet_hier.append(fchild)
    else:
        # At least one parent....
        abbrev_list = []
        for x in pids:
            fp = cdict[x]['facet_name']
            fbase = u'0/' + fp
            fchild = u'1/' + fp + u'/' + facet
            abbrev = fp + u'/' + facet
            abbrev_list.append(abbrev)
            aff_facet_hier.append(fbase)
            aff_facet_hier.append(fchild)
        abbrev = '; '.join(abbrev_list)
    return (abbrev, canon, aff_facet_hier, m_id)


class ADSAffilCelery(ADSCelery):

    def load_dicts(self, picklefile):
        # You need to initialize adict and cdict
        # in every ADSAffilCelery object you create
        # It's possible you'll get this when you (a)
        # don't have a pickle file, but (b) you're
        # about to, which is ok to pass.
        try:
            (self.adict, self.cdict) = utils.read_pickle(picklefile)
        except:
            pass

    def augment_affiliations(self, rec):
        try:
            self.adict
        except Exception as e:
            raise FatalException('adict/cdict not loaded, cannot continue.')

        # aff = affil record: list of all affil strings 
        #       of all authors in record
        aff = rec['aff']

        # initialize return arrays & unmatched dict
        abbreviation_list = []
        id_code_list = []
        canonical_list = []
        aff_facet_hier = []
        facet = []
        unmatched = {}

        # each s is one author's affil string
        for s in aff:
            # normalize the input string
            s = utils.reencode_string(utils.back_convert_entities(s)[0])
            if ';' in s:
                # if record contains ';', there are multiple affils
                # so split on the semicolon
                t = s.split(';')
                abb_list = []
                id_list = []
                can_list = []
                for v in t:
                    # each v is an affil among multiple for a given author
                    if v.strip() != '':
                        v = utils.reencode_string(utils.back_convert_entities(v)[0])
                        # call augmenter with substring v and the dicts
                        (aid, can, fac, idcode) = augmenter(v, self.adict, self.cdict)
                        abb_list.append(aid)
                        id_list.append(idcode)
                        can_list.append(can)
                        if fac:
                            facet.append(fac)
                        else:
                            if v != u'' and v !=u'-':
                                unmatched[v] = u'0'
#               if not isinstance(can_list, basestring):
                can_list = u'; '.join(can_list)
                abbreviation_list.append(u'; '.join(abb_list))
                id_code_list.append(u'; '.join(id_list))
                canonical_list.append(can_list)
            else:
                # call augmenter with string s and the dicts
                (aid, can, fac, idcode) = augmenter(s, self.adict, self.cdict)
                abbreviation_list.append(aid)
                id_code_list.append(idcode)
                canonical_list.append(can)
                if fac:
                    facet.append(fac)
                else:
                    if s != u'' and s !=u'-':
                    # if there is a real affstring (that isn't
                    # blank or "-") AND you can't match it,
                    # add it to unmatched.
                        unmatched[s] = u'0'

        # now create aff_facet_hier using similar logic,
        # whether single author or many, and whether
        # each author has one affil or many
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

#       rec['aff_abbrev'] = aff_facet_hier
        rec['aff_abbrev'] = abbreviation_list
        rec['aff_id'] = id_code_list
        rec['aff_canonical'] = canonical_list
        rec['aff_facet_hier'] = aff_facet_hier
        # the augmenter doesn't return data, but if strings aren't matched,
        # the unmatched strings are returned.
        return unmatched
