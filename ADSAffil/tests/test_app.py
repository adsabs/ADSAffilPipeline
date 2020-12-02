import os
import unittest
from ADSAffil import app, utils

stubdata_dir = os.path.dirname(app.__file__) + '/tests/stubdata'

class TestApp(unittest.TestCase):

    def test_create_base_instance(self):
        matcher = app.ADSAffilCelery()
        self.assertEqual(matcher.affdict, {})
        self.assertEqual(matcher.pcdict, {})
        self.assertEqual(matcher.clausedict, {})
        self.assertEqual(matcher.clause_crit, 0.75)
        self.assertEqual(matcher.separator, ',')
        self.assertFalse(matcher.exact)

    def test_create_working_instance(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery(self, affdict=adict, pcdict=cdict, 
                                     clausedict=clause_dict)

        rec = 'Department of Physics and Institute for the Early Universe, Ewha Womans University, Seodaaemun-gu, Seoul, South Korea'
        output_record = matcher.augment_affiliations(rec)
        expected_record = ('Ewha Wmns U/Inst Early Uni', 'Ewha Womans University, Institute for the Early Universe', ['0/Ewha Wmns U', '1/Ewha Wmns U/Inst Early Uni'], 'A11557')
        self.assertEqual(output_record, expected_record)


    def test_return_exact_matches(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery(self, affdict=adict, pcdict=cdict, 
                                     clausedict=clause_dict)

        rec = 'Department of Physics, University of Hanging Out and Listening to Jazz Records, Merced, CA'
        output_record = matcher.augment_affiliations(rec)
        expected_record = ('-', '-', None, '-')
        self.assertEqual(output_record, expected_record)


    def test_return_all_matches(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery(self, affdict=adict, pcdict=cdict, 
                                     clausedict=clause_dict)

        rec = 'Department of Physics, University of Hanging Out and Listening to Jazz Records, Merced, CA'

        matcher.clause_crit = 0.0
        expected_record = {'A05210': 0.25, 'A11557': 0.25, 'A00921': 0.25, 'A02585': 0.25, 'A03439': 0.75}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)

        matcher.clause_crit = 0.75
        expected_record = {'A03439': 0.75}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)
      
        matcher.clause_crit = 0.99
        expected_record = {}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)
      

    def test_find_matches_with_exact(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery(self, affdict=adict, pcdict=cdict, 
                                     clausedict=clause_dict)

        rec = 'Department of Physics and Institute for the Early Universe, Ewha Womans University, Seodaaemun-gu, Seoul, South Korea'
        output_record = matcher.find_matches(rec)
        expected_record = {'A11557': 2.0}
        self.assertEqual(output_record, expected_record)
