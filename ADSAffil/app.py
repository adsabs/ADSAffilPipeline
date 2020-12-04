from adsputils import ADSCelery
import ADSAffil.utils as utils


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

    def __init__(self, app_name, *args, **kwargs):
        super().__init__(app_name, *args, **kwargs)
        self.adict = {}
        self.cdict = {}
        self.clausedict = {}
        self.match_id = None
        self.separator = self.conf.CLAUSE_SEPARATOR
        self.crit = self.conf.SCORE_THRESHOLD
        self.exact = self.conf.EXACT_MATCHES_ONLY

    def _match_affil(self):
        output = dict()
        self._norm_affil()
        try:
            exact_id = self.adict[self.instring_norm]
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
                if v >= self.crit:
                    output[k] = v
        else:
            output[exact_id] = 2.
        return output

    def _output_affil(self):
        try:
            facet = self.cdict[self.match_id]['facet_name']
            pids = self.cdict[self.match_id]['parents']
            canon = self.cdict[self.match_id]['canonical_name']
        except Exception as notfound:
            # Not found in cdict -- can't ID affil string
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
                fp = self.cdict[x]['facet_name']
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
