import datetime
import re
from typing import (
    Dict,
    List,
    Union,
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
        # New transaction ids (original and proportion transaction)
        self.new_txs = set()
        # Updated transaction ids (original and proportion transaction)
        self.updated_txs = set()

    def _get(self, endpoint: str) -> requests.Response:
        resp = requests.get(
            f'{self.api_url}{endpoint}',
            headers=self.headers,
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(e)
            raise e
        return resp

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
            raise e
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

    def get_transaction(self, transaction_id: Union[int, str]) -> Dict:
        logger.debug(f'Getting transaction info for transaction id {transaction_id}')
        resp = self._get(endpoint=f'/transactions/{transaction_id}')
        resp.raise_for_status()
        return resp.json()['data']

    def update_transaction(self, tx_id: Union[int, str], transactions: List[Dict],
                           tx_title: str = None) -> requests.Response:
        """
            NOTE: For now this will just be used to update notes of a transaction.
            It might need expansion for broader support
        """
        logger.debug(f'Updating transaction id ({tx_id})...')

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

    def handle_incoming_transaction_data(self, data: Dict, is_new: bool) -> List[Dict]:
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
        if is_new:
            self.new_txs.add(tx_id)
        else:
            self.updated_txs.add(tx_id)

        new_txs = []

        # Iterate through splits; for any transaction split containing the tag pattern,
        #   build the criteria needed to create a new transaction for it
        for i, tx in enumerate(txs):
            tags = tx.get('tags')
            if not tags:
                tags = []
            for tag in tags:
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
                    is_updated = False
                    prop_tx_id = None
                    tx_notes = tx.get('notes') if tx.get('notes') is not None else ''
                    if current_notes := re.search(r'\w+\stx:\shttps?:\/\/.*\/show\/(\d+)', tx_notes):
                        logger.info('Transaction is an update that was previously handled by this process.')
                        # Existing note in transaction - likely updated
                        is_updated = True
                        prop_tx_id = current_notes.group(1)
                    raw_proportion = tag_match.group(1)
                    desc = tx.get('description')
                    if not content.get("group_title"):
                        title = f'Prop - {desc}'
                    else:
                        title = f'Prop - {content.get("group_title")}'
                    if raw_proportion.isnumeric():
                        proportion = float(raw_proportion) / 100
                        amount = round(float(tx.get('amount')) * proportion, 2)
                        new_txs.append({
                            'is_update': is_updated,
                            'new_tx': {
                                'title': title,
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
                                'prop_tx_id': prop_tx_id,
                                # The index of the split that was used.
                                #   For most transactions, this will always be 0
                                'index': i
                            }
                        })
        logger.info(f'{len(new_txs)} new transactions to make from transaction id {tx_id}')
        return new_txs

    def add_to_notes(self, transaction_data: Dict, split_index: int, new_transaction_id: int) -> str:
        org_notes = transaction_data['transactions'][split_index]['notes']
        tx_note = f'Proportion tx: {self.base_url}/transactions/show/{new_transaction_id}'
        if org_notes is None:
            org_notes = tx_note
        else:
            org_notes += f'\n{tx_note}'
        return org_notes

    def process_new_splits(self, new_splits: List[Dict], transaction_data: Dict):
        triggered_tx_id = transaction_data['id']

        for split in new_splits:
            if split.get('is_update'):
                # The main transaction was updated. Find the proportion transaction and update the amount
                self.process_updated_transaction(
                    triggered_tx_id=triggered_tx_id,
                    split=split
                )
            else:
                self.process_new_transaction(
                    triggered_tx_id=triggered_tx_id,
                    split=split,
                    transaction_data=transaction_data
                )

    def process_new_transaction(self, triggered_tx_id: int, split: Dict, transaction_data: Dict):
        """Creates a new proportional transaction, then updated the original, new transaction
            (that triggered this process) with that proportional transaction's details"""
        logger.info('Creating new transaction...')

        modified_splits = [{'transaction_journal_id': str(x['transaction_journal_id'])}
                           for x in transaction_data['transactions']]

        new_tx_resp = self.new_single_transaction(**split.get('new_tx'))
        new_tx_id = new_tx_resp.json()['data']['id']
        self.new_txs.add(new_tx_id)

        logger.info('Updating original transaction')
        split_tx_index = split['org_tx']['index']
        org_notes = self.add_to_notes(transaction_data=transaction_data, split_index=split_tx_index,
                                      new_transaction_id=new_tx_id)

        # Go through modified splits, find the tx with the matching journal id:
        for i, ms in enumerate(modified_splits):
            if ms['transaction_journal_id'] == split['org_tx']['tx_jrnl_id']:
                modified_splits[i]['notes'] = org_notes

        logger.debug(f'Modified note of original transaction to: "{org_notes}"')

        logger.info(f'Updating transaction id {triggered_tx_id} such: \n\t{modified_splits}')
        self.update_transaction(
            tx_id=triggered_tx_id,
            transactions=modified_splits
        )

    def process_updated_transaction(self, triggered_tx_id: int, split: Dict,):
        """Takes in an updated transaction's info and syncs it with
        the proportional transaction it links to via notes"""
        logger.info('Updating proportional transaction...')
        prop_tx_id = split['org_tx']['prop_tx_id']
        # Get proportional transaction data
        prop_tx_data = self.get_transaction(prop_tx_id)
        prop_txs = prop_tx_data['attributes']

        # Collect transaction journal ids
        modified_splits = []
        for ptx in prop_txs['transactions']:
            t_split_data = {'transaction_journal_id': str(ptx['transaction_journal_id'])}
            ptx_notes = ptx.get('notes') if ptx.get('notes') is not None else ''
            if re.search(fr'\w+\stx:\shttp://.*/show/{triggered_tx_id}', ptx_notes):
                # Notes had the link to our original transaction - this should be it.
                new_amount = split['new_tx']['amount']
                if ptx['amount'] == new_amount:
                    logger.info('Split matching notes did not have a changed proportional amount. Aborting.')
                    return
                else:
                    logger.info('Changing the amount for split matching notes...')
                    t_split_data['amount'] = new_amount
            else:
                logger.debug(f'No notes found matching the link to '
                             f'the original transaction id {triggered_tx_id}')
            modified_splits.append(t_split_data)

        self.updated_txs.add(prop_tx_id)

        logger.info(f'Updating transaction id {prop_tx_id} such: \n\t{modified_splits}')
        self.update_transaction(
            tx_id=prop_tx_id,
            transactions=modified_splits
        )
