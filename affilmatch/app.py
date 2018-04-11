import pandas as pd
from adsputils import ADSCelery
from adsmsg import AugmentAffiliationRequestRecord, \
    AugmentAffiliationRequestRecordList, \
    AugmentAffiliationResponseRecord, \
    AugmentAffiliationResponseRecordList


class ADSAugmentPipelineCelery(ADSCelery):
    """
    Tests the application's methods
    """

    def get_msg_type(self, msg):
        """
        Identifies the type of this supplied message.

        :param: Protobuf instance
        :return: str
        """
        print 'foo'
        if isinstance(msg, AugmentAffiliationRequestRecord):
            return 'affil_request'
        elif isinstance(msg, AugmentAffiliationRequestRecordList):
            return 'affil_requests'
        elif isinstance(msg, AugmentAffiliationResponseRecord):
            return 'affil_response'
        elif isinstance(msg, AugmentAffiliationResponseRecordList):
            return 'affil_responses'
        else:
            raise ValueError(
                'passed msg of invalid type %s, expected augment protobuf'
                % type(msg))

    def to_dataframe(self, message):
        """convert request protobuf to scikit dataframe"""
        message_type = self.get_msg_type(message)
        if message_type == 'affil_request':
            return pd.DataFrame([{'bibcode': message.bibcode,
                                  'Affil': message.affiliation,
                                  'Author': message.author,
                                  'sequence': message.sequence}])
        elif message_type == 'affil_requests':
            tmp = []
            for m in message.affiliation_requests:
                tmp.append({'bibcode': m.bibcode,
                            'Affil': m.affiliation,
                            'Author': m.author,
                            'sequence': m.sequence})
            return pd.DataFrame(tmp)
        else:
            raise ValueError(
                'to_dataframe does not handle message of type %s'
                % type(message))

    def to_response(self, request, answer, answer_id):
        """generate response protobuf to send to master pipeline"""
        message_type = self.get_msg_type(request)
        if message_type == 'affil_request':
            d = {'bibcode': request.bibcode,
                 'affiliation': request.affiliation,
                 'author': request.author,
                 'sequence': request.sequence,
                 'canonical_affiliation': answer,
                 'canonical_affiliation_id': answer_id}
            response = AugmentAffiliationResponseRecord(**d)
            return response
        elif message_type == 'affil_requests':
            response = AugmentAffiliationResponseRecordList()
            for r, a, id in zip(request.affiliation_requests, answer, answer_id):
                d = {'bibcode': r.bibcode,
                     'affiliation': r.affiliation,
                     'author': r.author,
                     'sequence': r.sequence,
                     'canonical_affiliation': a,
                     'canonical_affiliation_id': id}
                response.affiliation_responses.add(**d)
            return response
        else:
            raise ValueError(
                'to_response does not handle message of type %s'
                % type(request))
