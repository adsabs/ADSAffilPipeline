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
            # augment_affiliations can work on strings or json from protobuf
            # If rec is type str:
            if isinstance(rec,str):
                self.instring = rec
                self._norm_affil()
                return self._augmenter()
            # If rec is type dict (json from protobuf):
            elif isinstance(rec,dict):
                aff = rec['aff']
                abbreviation_list = []
                id_code_list = []
                canonical_list = []
                aff_facet_hier = []
                facet_list = []
                for s in aff: 
                    abb_list = []
                    id_list = []
                    can_list = []
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
                                # call augmenter with substring v and the dicts
                                self.instring = v
                                self._norm_affil()
                                (aid, can, fac, idcode) = self._augmenter()
                            abb_list.append(aid)
                            id_list.append(idcode)
                            can_list.append(can)
                            if fac:
                                facet_list.append(fac)
                        can_list = u'; '.join(can_list)
                        abbreviation_list.append(u'; '.join(abb_list))
                        id_code_list.append(u'; '.join(id_list))
                        canonical_list.append(can_list)
                    else:
                        # call augmenter with string s and the dicts
                        self.instring = s
                        self._norm_affil()
                        (aid, can, fac, idcode) = self._augmenter()
                        abbreviation_list.append(aid)
                        id_code_list.append(idcode)
                        canonical_list.append(can)
                        if fac:
                            facet_list.append(fac)

                # now create aff_facet_hier using similar logic,
                # whether single author or many, and whether
                # each author has one affil or many
                if len(facet_list) > 0:
                    f2 = []
                    for f in facet_list:
                        if len(f) == 1:
                            f2.append(f[0])
                        else:
                            for x in f:
                                f2.append(x)
                    try:
                        f4 = []
                        for f3 in list(dict.fromkeys(f2)):
                            if isinstance(f3, list):
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

                # Now you can write the augmented affil data...
                rec['aff_abbrev'] = abbreviation_list
                rec['aff_id'] = id_code_list
                rec['aff_canonical'] = canonical_list
                rec['aff_facet_hier'] = aff_facet_hier
                rec['aff_raw'] = rec['aff']
                rec['institution'] = rec['aff_abbrev']

            return rec
        else:
            return

    def find_matches(self, rec):
        if rec:
            self.instring = rec
            self._norm_affil()
        return self._match_affil()
