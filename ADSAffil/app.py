import ADSAffil.utils as utils
from adsputils import ADSCelery

class ADSAffilCelery(ADSCelery):

    def _norm_affil(self):
        if self.instring:
            self.instring = utils.clean_string(self.instring)
            self.clauses = utils.split_clauses(self.instring, 
                                               self.separator)
            if self.clauses:
                self.clauses_norm = [utils.normalize_string(clause)
                                     for clause in self.clauses]
            self.instring_norm = utils.normalize_string(self.instring)

    def __init__(self, instring = '', affdict={}, pcdict={}, clausedict={},
                 separator=',', exact = False, crit = 0.75, match_id = ''):
        self.affdict = affdict
        self.pcdict = pcdict
        self.clausedict = clausedict
        self.separator = separator
        self.exact = exact
        self.clause_crit = crit
        self.match_id = match_id
        if instring:
            self.instring = instring
            self._norm_affil()

    def _match_affil(self):
        output = dict()
        self._norm_affil()
        try:
            self.exact_id = self.affdict[self.instring_norm]
        except Exception as nomatch:
            test_dict = dict()
            if not self.exact:
                nc = len(self.clauses_norm)
                for c in self.clauses_norm:
                    if c in self.clausedict:
                        for k in self.clausedict[c]:
                            if k in test_dict:
                                test_dict[k] += 1./nc
                            else:
                                test_dict[k] = 1./nc
            for k, v in test_dict.items():
                if v >= self.clause_crit:
                    output[k] = v
        else:
            output[self.exact_id] = 2.
        return output

    def _output_affil(self):
        try:
            facet = self.pcdict[self.match_id]['facet_name']
            pids = self.pcdict[self.match_id]['parents']
            canon = self.pcdict[self.match_id]['canonical_name']
        except Exception as notfound:
            # Not found in cdict -- can't ID affil string
            self.logger.debug('output_affil: %s, returning empty affil' % notfound)
            return ('-', '-', None, '-')
        aff_facet_hier = []
        if pids[0] == '-':
            # No parents...
            fbase = '0/' + facet
            fchild = '1/' + facet + '/' + facet
            abbrev = facet + '/' + facet
            aff_facet_hier.append(fbase)
            aff_facet_hier.append(fchild)
        else:
            # At least one parent....
            abbrev_list = []
            for x in pids:
                fp = self.pcdict[x]['facet_name']
                fbase = '0/' + fp
                fchild = '1/' + fp + '/' + facet
                abbrev = fp + '/' + facet
                abbrev_list.append(abbrev)
                aff_facet_hier.append(fbase)
                aff_facet_hier.append(fchild)
            abbrev = '; '.join(abbrev_list)
        return (abbrev, canon, aff_facet_hier, self.match_id)


    def _augmenter(self):
        outrec = ('-', '-', None, '-')
        try:
            result = self._match_affil()
            (m_id, m_score) = list(result.items())[0]
            if m_id and m_score == 2.0:
                self.match_id = m_id
                outrec = self._output_affil()
        except Exception as nomatch:
            pass
        return outrec


    def augment_affiliations(self, rec):
        if rec:
            self.instring = rec
            self._norm_affil()
        return self._augmenter()


    def find_matches(self, rec):
        if rec:
            self.instring = rec
            self._norm_affil()
        return self._match_affil()
