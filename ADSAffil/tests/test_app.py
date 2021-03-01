import json
import os
import unittest
from ADSAffil import app, utils

stubdata_dir = os.path.dirname(app.__file__) + '/tests/stubdata'

class TestApp(unittest.TestCase):

    def test_create_base_instance(self):
        matcher = app.ADSAffilCelery('augment-pipeline')
        self.assertEqual(matcher.adict, {})
        self.assertEqual(matcher.cdict, {})
        self.assertEqual(matcher.clausedict, {})
        self.assertEqual(matcher.crit, 0.75)
        self.assertEqual(matcher.separator, ',')
        self.assertFalse(matcher.exact)

    def test_create_working_instance(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery('foo')
        matcher.adict = adict
        matcher.cdict = cdict
        matcher.clausedict = clause_dict

        # first test: use augment_affiliations to exactly match a string:
        rec = 'Department of Physics and Institute for the Early Universe, Ewha Womans University, Seodaaemun-gu, Seoul, South Korea'
        output_record = matcher.augment_affiliations(rec)
        expected_record = ('Ewha Wmns U/Inst Early Uni', 'Ewha Womans University, Institute for the Early Universe', ['0/Ewha Wmns U', '1/Ewha Wmns U/Inst Early Uni'], 'A11557')
        self.assertEqual(output_record, expected_record)

        # second test: use augment_affiliations to augment a record
        test_json = stubdata_dir + '/record.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        output_record = matcher.augment_affiliations(rec)
        expected_record = {'bibcode': '2002ApJ...576..963T', 'aff': ['Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101'], 'aff_abbrev': ['Yale U/Dep Ast', 'Yale U/Dep Ast', 'Yale U/Dep Ast'], 'aff_id': ['A00928', 'A00928', 'A00928'], 'aff_canonical': ['Yale University, Department of Astronomy', 'Yale University, Department of Astronomy', 'Yale University, Department of Astronomy'], 'aff_facet_hier': ['0/Yale U', '1/Yale U/Dep Ast'], 'aff_raw': ['Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101'], 'institution': ['Yale U/Dep Ast', 'Yale U/Dep Ast', 'Yale U/Dep Ast']}
        self.assertEqual(output_record, expected_record)

        # third test: try augmenting a record with some unmatched affs:
        test_json = stubdata_dir + '/record2.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        output_record = matcher.augment_affiliations(rec)
        expected_record = {'bibcode': '2021FOO...576..963T', 'aff': ['University of Unbridled Nonsense', 'University of Irrational Exuberance', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101'], 'aff_abbrev': ['-', '-', 'Yale U/Dep Ast'], 'aff_id': ['-', '-', 'A00928'], 'aff_canonical': ['-', '-', 'Yale University, Department of Astronomy'], 'aff_facet_hier': ['0/Yale U', '1/Yale U/Dep Ast'], 'aff_raw': ['University of Unbridled Nonsense', 'University of Irrational Exuberance', 'Astronomy Department, Yale University, P.O. Box 208101, New Haven, CT 06520-8101'], 'institution': ['-', '-', 'Yale U/Dep Ast']}
        self.assertEqual(output_record, expected_record)

        # fourth test: try augmenting a record with all unmatched affs:
        test_json = stubdata_dir + '/record3.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        output_record = matcher.augment_affiliations(rec)
        expected_record = {'bibcode': '2021FUBAR.576..963T', 'aff': ['University of Unbridled Nonsense', 'University of Irrational Exuberance', 'University of Mass Hysteria'], 'aff_abbrev': ['-', '-', '-'], 'aff_id': ['-', '-', '-'], 'aff_canonical': ['-', '-', '-'], 'aff_facet_hier': [], 'aff_raw': ['University of Unbridled Nonsense', 'University of Irrational Exuberance', 'University of Mass Hysteria'], 'institution': ['-', '-', '-']}
        self.assertEqual(output_record, expected_record)
 
        # fifth test: try augmenting a record with empty affs:
        test_json = stubdata_dir + '/record4.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        output_record = matcher.augment_affiliations(rec)
        expected_record = {'bibcode': '2021BAZ...576..963T', 'aff': [], 'aff_abbrev': [], 'aff_id': [], 'aff_canonical': [], 'aff_facet_hier': [], 'aff_raw': [], 'institution': []}
        self.assertEqual(output_record, expected_record)
 
        # sixth test: try augmenting a record with blank affs:
        test_json = stubdata_dir + '/record5.json'
        with open(test_json,'r') as fj:
            jdata = json.load(fj)
        rec = jdata['response']['docs'][0]
        output_record = matcher.augment_affiliations(rec)
        print(output_record)
        expected_record = {'bibcode': '2021ASDFQ.576..963T', 'aff': ['-'], 'aff_abbrev': ['-'], 'aff_id': ['-'], 'aff_canonical': ['-'], 'aff_facet_hier': [], 'aff_raw': ['-'], 'institution': ['-']}
        self.assertEqual(output_record, expected_record)
 

    def test_return_exact_matches(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery('augment-pipeline') 
        matcher.adict = adict
        matcher.cdict = cdict
        matcher.clausedict = clause_dict

        rec = 'Department of Physics, University of Hanging Out and Listening to Jazz Records, Merced, CA'
        output_record = matcher.augment_affiliations(rec)
        expected_record = ('-', '-', None, '-')
        self.assertEqual(output_record, expected_record)


    def test_return_all_matches(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery('fnord')
        matcher.adict = adict
        matcher.cdict = cdict
        matcher.clausedict = clause_dict

        rec = 'Department of Physics, University of Hanging Out and Listening to Jazz Records, Merced, CA'

        matcher.crit = 0.0
        expected_record = {'A05210': 0.25, 'A11557': 0.25, 'A00921': 0.25, 'A02585': 0.25, 'A03439': 0.75}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)

        matcher.crit = 0.75
        expected_record = {'A03439': 0.75}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)
      
        matcher.crit = 0.99
        expected_record = {}
        output_record = matcher.find_matches(rec)
        self.assertEqual(output_record, expected_record)
      

    def test_find_matches_with_exact(self):
        aff_pickle_filename = stubdata_dir + '/aff.pickle'
        (adict, cdict) = utils.load_affil_dict(aff_pickle_filename)
        clause_pickle_filename = stubdata_dir + '/clause.pickle'
        clause_dict = utils.load_clause_dict(clause_pickle_filename)

        matcher = app.ADSAffilCelery('augment-pipeline')
        matcher.adict = adict
        matcher.cdict = cdict
        matcher.clausedict = clause_dict

        rec = 'Department of Physics and Institute for the Early Universe, Ewha Womans University, Seodaaemun-gu, Seoul, South Korea'
        output_record = matcher.find_matches(rec)
        expected_record = {'A11557': 2.0}
        self.assertEqual(output_record, expected_record)


