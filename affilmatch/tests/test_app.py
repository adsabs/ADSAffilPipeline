#!/usr/bin/env python

import unittest
import os
import run as app
import pandas as pd
from pandas.util.testing import assert_frame_equal

TEST_DATA=os.path.abspath('test_data')
class TestReadData(unittest.TestCase):

    def test_normal(self):
        infile = "test_data/gtest_dict.txt"
        incols = ['A','B']
        outdf=pd.DataFrame({'A':pd.Series(['1000','2000'],index=[0,1]),
                           'B':pd.Series(['hello nice day goodbye',
                                          'yes no maybe definitely'],
                                          index=[0,1])})
        indf=app.read_data(infile,incols)
        assert_frame_equal(indf,outdf)

    def test_nocolumns(self):
        infile="test_data/gtest_dict.txt"
        with self.assertRaises(NameError):
            indf=app.read_data(infile,incols)


    def test_nofile(self):
        incols=['A','B']
        infile="no_such_file"
        with self.assertRaises(IOError):
            app.read_data(infile,incols)

    def test_lockedfile(self):
        incols=['A','B']
        infile="test_data/glocked_file.txt"
        with self.assertRaises(IOError):
            app.read_data(infile,incols)


class TestColToList(unittest.TestCase):

    def test_normal(self):
        inlist=['1000','2000']
        testdf=pd.DataFrame({'A':pd.Series(['1000','2000'],index=[0,1]),
                           'B':pd.Series(['hello nice day goodbye',
                                          'yes no maybe definitely'],
                                          index=[0,1])})
        outlist=app.column_to_list(testdf,'A')
        self.assertEqual(inlist,outlist)

    def test_wrongtype(self):
        inlist=['1000','2000']
        testdf=0
        with self.assertRaises(TypeError):
            outlist=app.column_to_list(testdf,'A')
        
    def test_badcolumn(self):
        inlist=['1000','2000']
        testdf=pd.DataFrame({'A':pd.Series(['1000','2000'],index=[0,1]),
                           'B':pd.Series(['hello nice day goodbye',
                                          'yes no maybe definitely'],
                                          index=[0,1])})
        with self.assertRaises(KeyError):
            outlist=app.column_to_list(testdf,'C')
        
        
class TestGetParent(unittest.TestCase):

    def test_badaffil(self):
        affil='999999'
        parents={'1234':'test 1','2345':'test 2'}
        with self.assertRaises(KeyError):
            out=app.get_parent(parents[affil],parents)

    def test_nodict(self):
        affil='123'
        with self.assertRaises(NameError):
            out=app.get_parent(parents[affil],parents)

    def test_baddict(self):
        affil='123'
        parents=0
        with self.assertRaises(TypeError):
            out=app.get_parent(parents[affil],parents)

    def test_emptycall(self):
        with self.assertRaises(TypeError):
            out=app.get_parent()


class TestGetOptions(unittest.TestCase):

    def test_noopts(self):
        with self.assertRaises(SystemExit):
            variable=app.get_arguments()


if __name__ == '__main__':
    unittest.main()
