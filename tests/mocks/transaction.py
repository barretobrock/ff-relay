from typing import (
    Dict,
    List,
    Optional,
    Union
)

from ..common import (
    random_float,
    random_int,
    random_string
)


DEFAULT_DEST_ID = 20
DEFAULT_SOURCE_ID = 40


def make_transaction_journal(
        tjid: int = None,
        tx_type: str = 'withdrawal',
        amount: Union[float, str] = None,
        desc: str = None,
        notes: str = None,
        tags: List[str] = None,
        source_id: int = DEFAULT_SOURCE_ID,
        dest_id: int = DEFAULT_DEST_ID
) -> Dict:
    if tjid is None:
        tjid = random_int(600, 1000)
    if amount is None:
        amount = str(round(random_float(10, 200), 2))
    if desc is None:
        desc = 'Test ' + random_string(50)

    return {
        'user': 1,
        'transaction_journal_id': tjid,
        'type': tx_type,
        'date': '2024-06-24T12:34:00-05:00',
        'order': 0,
        'currency_id': 8,
        'currency_code': 'USD',
        'currency_symbol': '$',
        'currency_decimal_places': 2,
        'foreign_currency_id': None,
        'foreign_currency_code': None,
        'foreign_currency_symbol': None,
        'foreign_currency_decimal_places': None,
        'amount': amount,
        'foreign_amount': None,
        'description': desc,
        'source_id': source_id,
        'source_name': 'SOME BANK',
        'source_iban': '',
        'source_type': 'Asset account',
        'destination_id': dest_id,
        'destination_name': 'Some Store',
        'destination_iban': None,
        'destination_type': 'Expense account',
        'budget_id': None,
        'budget_name': None,
        'category_id': None,
        'category_name': None,
        'bill_id': None,
        'bill_name': None,
        'reconciled': False,
        'notes': notes,
        'tags': tags,
        'internal_reference': None,
        'external_id': None,
        'original_source': 'ff3-v6.1.16|api-v2.1.0',
        'recurrence_id': None,
        'bunq_payment_id': None,
        'import_hash_v2': '3241234234234',
        'sepa_cc': None,
        'sepa_ct_op': None,
        'sepa_ct_id': None,
        'sepa_db': None,
        'sepa_country': None,
        'sepa_ep': None,
        'sepa_ci': None,
        'sepa_batch_id': None,
        'interest_date': None,
        'book_date': None,
        'process_date': None,
        'due_date': None,
        'payment_date': None,
        'invoice_date': None,
        'longitude': None,
        'latitude': None,
        'zoom_level': None
    }


def make_new_transaction_event(
    txs: List[Optional[Dict]] = None,
    tid: int = None,
) -> Dict:

    if txs is None:
        txs = [{'tjid': None}]
    if tid is None:
        tid = random_int(200, 500)

    return {
        'uuid': '24efb4f1-b140-451a-9272-76c49dd3fafa',
        'user_id': 1,
        'trigger': 'STORE_TRANSACTION',
        'response': 'TRANSACTIONS',
        'url': 'http://some.site/transaction/add',
        'version': 'v0',
        'content': {
            'id': tid,
            'created_at': '2024-06-24T12:34:39-05:00',
            'updated_at': '2024-06-24T12:34:39-05:00',
            'user': 1,
            'group_title': None,
            'transactions': [make_transaction_journal(**x) for x in txs],
            'links': [
                {
                    'rel': 'self',
                    'uri': f'/transactions/{tid}'
                }
            ]
        }
}