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

    def test_handle_new_single_transaction_data(self):
        tx_info_list = [{'tags': ['something-p36']}]
        tx_event = make_new_transaction_event(txs=tx_info_list)

        new_txs = self.ffr.handle_incoming_transaction_data(data=tx_event, is_new=True)
        self.assertIsInstance(new_txs, list)
        self.assertEqual(len(tx_info_list), len(new_txs))
        for new_tx in new_txs:
            self.assertFalse(new_tx['is_update'])
            self.assertIn(new_tx['org_tx']['id'], self.ffr.new_txs)

    def test_handle_update_single_transaction_data(self):
        tx_info_list = [{'tags': ['something-p36'], 'notes': 'My tx: {ff-base-url}/show/44'.format(**self.props)}]
        tx_event = make_new_transaction_event(txs=tx_info_list)

        new_txs = self.ffr.handle_incoming_transaction_data(data=tx_event, is_new=False)
        self.assertIsInstance(new_txs, list)
        self.assertEqual(len(tx_info_list), len(new_txs))
        for new_tx in new_txs:
            self.assertTrue(new_tx['is_update'])
            self.assertIn(new_tx['org_tx']['id'], self.ffr.updated_txs)
            # original transaction info
            org_tx = new_tx['org_tx']
            tx = tx_event['content']['transactions'][0]
            self.assertEqual(str(tx['transaction_journal_id']), org_tx['tx_jrnl_id'])


if __name__ == '__main__':
    main()
