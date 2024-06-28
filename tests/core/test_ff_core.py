from datetime import datetime
from typing import Tuple
from unittest import (
    TestCase,
    main,
)
from unittest.mock import MagicMock

from pukr import get_logger

from ffrelay.core.ff_core import FireFlyRelayCore

from tests.common import (
    make_patcher,
    random_string,
)
from tests.mocks.transaction import (
    make_new_transaction_event,
    DEFAULT_DEST_ID,
    DEFAULT_SOURCE_ID
)


class TestFFRCore(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.log = get_logger('test_ff_core')

    def setUp(self) -> None:
        self.mock_req = make_patcher(self, 'ffrelay.core.ff_core.requests')
        self.props = {
            'ff-base-url': 'https://example.com',
            'token': 'hello-token',
            'owe-acct-id': DEFAULT_DEST_ID,
            'inc-acct-id': DEFAULT_SOURCE_ID,
            'currency-code': 'USD'
        }

        self.ffr = FireFlyRelayCore(props=self.props)

    def test_init(self):

        self.assertDictEqual(self.props, self.ffr.props)

    def test_handle_transaction_data(self):
        tx_event = make_new_transaction_event()

        self.ffr.handle_incoming_transaction_data(data=tx_event)


if __name__ == '__main__':
    main()
