#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
from adsmsg import AugmentAffiliationRequestRecord, \
    AugmentAffiliationRequestRecordList, \
    AugmentAffiliationResponseRecord, \
    AugmentAffiliationResponseRecordList
from affilmatch import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.ADSAugmentPipelineCelery('test')

    def test_get_msg_type(self):
        d = {'bibcode': '2003ASPC..295..361M',
             'status': 2,
             'affiliation': 'University of Deleware',
             'author': 'Stephen McDonald',
             'sequence': '1/2'}
        a = AugmentAffiliationRequestRecord(**d)
        t = self.app.get_msg_type(a)
        self.assertEqual(t, 'affil_request')
        a = AugmentAffiliationRequestRecordList()
        t = self.app.get_msg_type(a)
        self.assertEqual(t, 'affil_requests')
        a = AugmentAffiliationResponseRecord()
        t = self.app.get_msg_type(a)
        self.assertEqual(t, 'affil_response')
        a = AugmentAffiliationResponseRecordList()
        t = self.app.get_msg_type(a)
        self.assertEqual(t, 'affil_responses')

    def test_to_dataframe(self):
        """create protobuf and verify conversion to DataFrame"""
        d = {'bibcode': '2003ASPC..295..361M',
             'status': 2,
             'affiliation': 'Center for Astrophysics',
             'author': 'Stephen McDonald',
             'sequence': '1/2'}
        a = AugmentAffiliationRequestRecord(**d)
        df = self.app.to_dataframe(a)
        self.assertEqual(d['bibcode'], df['bibcode'][0])
        self.assertEqual(d['affiliation'], df['Affil'][0])
        self.assertEqual(d['author'], df['Author'][0])
        self.assertEqual(d['sequence'], df['sequence'][0])

    def test_to_response(self):
        d = {'bibcode': '2003ASPC..295..361M',
             'status': 2,
             'affiliation': 'Center for Astrophysics',
             'author': 'Stephen McDonald',
             'sequence': '1/2'}
        a = AugmentAffiliationRequestRecord(**d)
        answer = ('foo')
        answer_id = ('1')
        response = self.app.to_response(a, answer, answer_id)
        self.assertEqual(a.bibcode, response.bibcode)
        
