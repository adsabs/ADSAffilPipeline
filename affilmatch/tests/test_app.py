#!/usr/bin/env python

import unittest

from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationRequestRecordList, AugmentAffiliationResponseRecord, AugmentAffiliationResponseRecordList
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
