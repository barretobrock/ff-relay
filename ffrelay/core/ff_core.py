import datetime
import re
from typing import (
    Dict,
    Union,
    List
)

from loguru import logger
import pytz
import requests


class FireFlyRelayCore:

    def __init__(self, props: Dict):
        url = props.get('ff-base-url')

        self.base_url = url
        self.api_url = f'{url}/api/v1'
        token = props.pop('token')
        self.headers = {
            'accept': 'application/vnd.api+json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.props = props
        self.new_original_txs = set()
        self.new_prop_txs = set()
        self.list_of_txs_to_update = []

    def _post(self, endpoint: str, data: Dict) -> requests.Response:
        resp = requests.post(
            f'{self.api_url}{endpoint}',
            headers=self.headers,
            json=data
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(e)
            logger.warning(data)
        return resp

    def _put(self, endpoint: str, data: Dict) -> requests.Response:
        resp = requests.put(
            f'{self.api_url}{endpoint}',
            headers=self.headers,
            json=data
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(e)
            logger.warning(data)
            raise e
        return resp

    def new_single_transaction(
            self,
            title: str,
            tx_type: str,
            amount: float,
            desc: str,
            source_acct_id: int = None,
            dest_acct_id: int = None,
            tx_date: Union[datetime.datetime, datetime.date] = None,
            notes: str = None,
            tags: List[str] = None,
            currency: str = 'USD'
    ):
        if tx_date is None:
            tx_date = datetime.datetime.now(tz=pytz.timezone("US/Central"))
        elif isinstance(tx_date, datetime.date):
            tx_date = datetime.datetime.combine(tx_date, datetime.time.min, tzinfo=pytz.timezone("US/Central"))

        tx_date_str = tx_date.strftime('%FT%T%z')

        resp = self._post(
            endpoint='/transactions',
            data={
                "error_if_duplicate_hash": True,
                "apply_rules": False,
                "fire_webhooks": False,
                "group_title": title,
                "transactions": [
                    {
                        "type": tx_type,
                        "date": tx_date_str,
                        "amount": str(amount),
                        "description": desc,
                        "order": 0,
                        "currency_code": currency,
                        "source_id": str(source_acct_id),
                        "destination_id": str(dest_acct_id),
                        "reconciled": False,
                        "tags": tags,
                        "notes": notes,
                    }
                ]
            }
        )
        return resp

    def update_transaction(self, tx_id: Union[int, str], transactions: List[Dict],
                           tx_title: str = None) -> requests.Response:
        """
            NOTE: For now this will just be used to update notes of a transaction.
            It might need expansion for broader support
        """
        logger.debug(f'Updating tx ({tx_id})...')

        resp = self._put(
            endpoint=f'/transactions/{tx_id}',
            data={
                "apply_rules": False,
                "fire_webhooks": False,
                "group_title": tx_title,
                "transactions": transactions
            }
        )

        resp.raise_for_status()
        return resp

    def handle_incoming_transaction_data(self, data: Dict) -> List[Dict]:
        """
            Takes in incoming transaction data, determines if any meet the tag criteria for
             proportion-based replication. Outputs a list of dicts of new transactions to make
             (and original transaction details to update)
        """
        logger.info('Receiving data for transaction...')
        logger.info(data)
        content = data['content']
        tx_id = content['id']
        txs = content['transactions']
        logger.info(f'Transaction id: {tx_id}')
        self.new_original_txs.add(tx_id)

        new_txs = []

        # Iterate through splits; for any transaction split containing the tag pattern,
        #   build the criteria needed to create a new transaction for it
        for i, tx in enumerate(txs):
            for tag in tx.get('tags', []):
                """
                    ⠀ ⣠⠴⠶⠦⣄⠀⠀⣠⠤⢤⡀⠀⢀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⢸⠱⠀⠀⠀⠈⢧⡞⠁⠀⠀⢹⡴⠋⠀⠀⠈⠳⡀⠀⠀⠀⠀⠀⠀
                ⠀⠀⣀⣀⣘⣆⡑⡀⠀⠀⠘⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⣧⠴⠲⢦⡀⠀⠀
                ⣰⢻⠉⠀⠀⠈⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⡇⠀⠀
                ⡇⢠⠀⠀⠀⠀⠀⠀NITH⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣃⠀⠀
                ⢧⡀⠑⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀        ⠐⠉⠉⠹⡄
                ⠈⢿⣷⠖⠀⠀⠀⠀⠀⠀⠀⠀⠀WALRUTH!⠀⠀⠀⠀⠀⠀⠀⢠⠇
                ⠀⢰⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣶⣿⠀
                ⠀⠸⡄⠢⢀⠀⡀⠠⡄⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠋⠁⠀
                ⠀⠀⢹⣶⣤⣤⣴⣇⠐⢄⠀⠀⡀⣾⠀⢀⠀⠀⠀⣀⠀⠀⠀⣂⣴⡏⠀⠀⠀
                ⠀⠀⠀⠉⠛⠛⠋⠙⣷⣤⣠⣤⣾⠏⢷⣄⣈⣩⣵⡘⢄⠀⠀⡿⠛⠁⠀⠀⠀⠀___
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣷⣦⠽⣦⠀  .-9 9 `\\
                                                 =(:(::)=  ;
                                                   ||||     \\
                                                   ||||      `-.
                                                  ,\|\|         `,
                                                 /                \\
                                                ;                  `'---.,
                                                |                         `\
                                                ;                     /     |
                                                \                    |      /
                                                )           \  __,.--\    /
                                              .-' \,..._\     \`   .-'  .-'
                                             `-=``      `:    |   /-/-/`
                                                         `.__/
                """
                if tag_match := re.match(r'\w+-p(\d+)', tag):
                    raw_proportion = tag_match.group(1)
                    desc = tx.get('description')
                    if raw_proportion.isnumeric():
                        proportion = float(raw_proportion) / 100
                        amount = round(float(tx.get('amount')) * proportion, 2)
                        new_txs.append({
                            'new_tx': {
                                'title': f'Mprop - {content["group_title"]}',
                                'tx_type': 'deposit' if tx.get('type') == 'withdrawal' else 'withdrawal',
                                'amount': str(amount),
                                'desc': desc,
                                'source_acct_id': self.props.get('inc-acct-id'),
                                'dest_acct_id': self.props.get('owe-acct-id'),
                                'notes': f'From tx: {self.base_url}/transactions/show/{tx_id}'
                            },
                            'org_tx': {
                                # The main transaction
                                'id': tx_id,
                                'tx_jrnl_id': str(tx.get('transaction_journal_id')),
                                # The index of the split that was used.
                                #   For most transactions, this will always be 0
                                'index': i
                            }
                        })
        logger.info(f'{len(new_txs)} new transactions to make from transaction id {tx_id}')
        return new_txs


