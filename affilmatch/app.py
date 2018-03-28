from adsputils import ADSCelery
import os
from adsmsg import AugmentAffiliationRequestRecord, AugmentAffiliationRequestRecordList, AugmentAffiliationResponseRecord, AugmentAffiliationResponseRecordList

class ADSAugmentCelery(ADSCelery):


    def get_msg_type(self, msg):
        """Identifies the type of this supplied message.

        :param: Protobuf instance
        :return: str
        """
        if isinstance(msg, AugmentAffiliationRequestRecord):
            return 'affil_request'
        elif isinstance(msg, AugmentAffiliationRequestRecordList):
            return 'affil_requests'
        elif isinstance(msg, AugmentAffiliationResponseRecord):
            return 'affil_response'
        elif isinstance(msg, AugmentAffiliationResponseRecordList):
            return 'affil_responses'
        else:
            raise ValueError('passed msg of invalid type %s, expected augment protobuf' % type(msg))
