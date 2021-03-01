import filecmp
import os
import unittest
from ADSAffil import utils

stubdata_dir = os.path.dirname(utils.__file__) + '/tests/stubdata'

class TestUtils(unittest.TestCase):

    def test_clean_string(self):

        test_input = ";; Hello, &epsilon;; My ; ; name is ;; ; Matthew;"
        expected_output = "Hello, ε; My ; name is ; Matthew"

        test_output = utils.clean_string(test_input)
        self.assertEqual(expected_output, test_output)

    def test_normalize_dict(self):

        test_input_dict = {'Center for Astrophysics | Harvard & Smithsonian, 60 Garden St., MS83, Cambridge, MA 02138': 'A01400'}
        expected_output_dict = {'CENTER FOR ASTROPHYSICS | HARVARD & SMITHSONIAN 60 GARDEN ST MS83 CAMBRIDGE MA 02138': 'A01400'}

        test_output_dict = utils.normalize_dict(test_input_dict)
        self.assertEqual(expected_output_dict, test_output_dict)

    def test_create_clause_dict(self):

        test_input_dict = {'Center for Astrophysics | Harvard & Smithsonian, 60 Garden St., MS83, Cambridge, MA 02138': 'A01400'}
        expected_output_dict = {'60 GARDEN ST': ['A01400'], 'CAMBRIDGE': ['A01400'], 'CENTER FOR ASTROPHYSICS | HARVARD & SMITHSONIAN': ['A01400'], 'MA 02138': ['A01400'], 'MS83': ['A01400']}

        test_output_dict = utils.create_clause_dict(test_input_dict)
        self.assertEqual(expected_output_dict, test_output_dict)


    def test_load_affils_affdict_file(self):

        infile = 'this_file_does_not_exist.txt'
        self.assertRaises(utils.AffilTextFileException,utils.load_affils_affdict_file, infile)

        infile = stubdata_dir + '/affil_strings.txt'
        affdict = utils.load_affils_affdict_file(infile)

        instring = 'Center for Photonic Materials and Devices, Department of Physics, Fisk University, Nashville, TN 37208, USA'
        expected_id = 'A00921'
        self.assertEqual(expected_id, affdict[instring])

        instring = 'This is not an affiliation id.'
        self.assertRaises(KeyError, lambda: affdict[instring])


    def test_load_affils_pcdict_file(self):

        infile = 'this_file_does_not_exist.txt'
        self.assertRaises(utils.PCTextFileException,utils.load_affils_pcdict_file, infile)

        infile = stubdata_dir + '/parent_child.txt'
        canondict = utils.load_affils_pcdict_file(infile)
        result = canondict['A01400']
        expected_output = {'canonical_name': 'Harvard Smithsonian Center for Astrophysics', 'facet_name': 'CfA', 'parents': ['A00211', 'A01397'], 'children': ['-']}
        self.assertEqual(result, expected_output)


    def test_affil_pickling(self):

        pc_file = stubdata_dir + '/parent_child.txt'
        pickle_file = 'aff.pickle'
        protocol = 4
        expected_file = stubdata_dir + '/aff.pickle'

        affil_file = 'wrong_filename.txt'
        self.assertRaises(utils.MakeAffilPickleException, utils.make_affil_pickle, affil_file, pc_file, pickle_file, protocol)

        affil_file = stubdata_dir + '/affil_strings.txt'
        utils.make_affil_pickle(affil_file, pc_file, pickle_file, protocol)
        self.assertTrue(filecmp.cmp(pickle_file, expected_file))

        (aff_dict, pc_dict) = utils.load_affil_dict(pickle_file)

        test_string = 'Institute for the Early Universe, Ewha Womans University &amp; Advanced Academy, Seoul, Korea'
        expected_output = 'A11557'
        # It should fail if you don't clean and normalize the string first
        self.assertRaises(KeyError, lambda: aff_dict[test_string])
        test_string = utils.normalize_string(utils.clean_string(test_string))
        self.assertEqual(expected_output, aff_dict[test_string])

        test_id = 'A05210'
        expected_output = {'canonical_name': 'University of Tirana, Albania', 'children': ['-'], 'facet_name': 'U Tirana', 'parents': ['-']}
        self.assertEqual(expected_output, pc_dict[test_id])
        if os.path.isfile(pickle_file):
            os.remove(pickle_file)



## This test isn't working as expected, and I think it's because the function
## has a list(set(list())) command in it -- that's not guaranteed to retain
## the order of a list.
    def test_make_clause_pickle(self):
        affil_file = stubdata_dir + '/affil_strings.txt'
        pickle_file = 'clause.pickle'
        separator = ','
        protocol = 4
        expected_file = stubdata_dir + '/clause.pickle'
        utils.make_clause_pickle(affil_file, pickle_file, separator, protocol)
        self.assertTrue(filecmp.cmp(pickle_file, expected_file))
        os.remove(pickle_file)


    def test_clause_pickling(self):

        pickle_file = 'clause.pickle'
        separator = ','
        protocol = 4

        affil_file = 'wrong_filename.txt'
        self.assertRaises(utils.MakeClausePickleException, utils.make_clause_pickle, affil_file, pickle_file, separator, protocol)

        affil_file = stubdata_dir + '/affil_strings.txt'
        utils.make_clause_pickle(affil_file, pickle_file, separator, protocol)
        
        clause_dict = utils.load_clause_dict(pickle_file)
        test_string = utils.normalize_string('Department of Physics')
        test_results = clause_dict[test_string]
        test_results.sort()
        expected_results = ['A00921', 'A02585', 'A03439', 'A05210', 'A11557']
        self.assertEqual(test_results, expected_results)
        if os.path.isfile(pickle_file):
            os.remove(pickle_file)
