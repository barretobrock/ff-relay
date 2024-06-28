from flask import (
    Blueprint,
    current_app,
    request,
    jsonify
)

from ffrelay.routes.helpers import (
    get_app_logger,
    get_ffr_core
)

bp_trans = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp_trans.route('/add', methods=['GET', 'POST'])
def add_transaction():
    log = get_app_logger()
    ffrcore = get_ffr_core()

    data = request.get_json()
    tx_data = data['content']

    triggered_tx_id = tx_data['id']
    if triggered_tx_id in ffrcore.new_txs:
        # Transaction already handled - skip
        log.info(f'Skipping new transaction - already worked on tx id: {triggered_tx_id}')
        return 'OK', 200

    new_txs = ffrcore.handle_incoming_transaction_data(data=data, is_new=True)

    if len(new_txs) == 0:
        log.debug('No transactions with matching tags found!')
        return 'OK', 200

    ffrcore.process_new_splits(
        new_splits=new_txs,
        transaction_data=tx_data
    )
    return 'OK', 200


@bp_trans.route('/update', methods=['GET', 'POST'])
def update_transaction():
    log = get_app_logger()
    ffrcore = get_ffr_core()

    data = request.get_json()
    tx_data = data['content']

    triggered_tx_id = tx_data['id']
    if triggered_tx_id in ffrcore.updated_txs:
        # Transaction already handled - skip
        log.info(f'Skipping updated transaction - already worked on tx id: {triggered_tx_id}')
        return 'OK', 200

    new_txs = ffrcore.handle_incoming_transaction_data(data=data, is_new=False)

    if len(new_txs) == 0:
        log.debug('No transactions with matching tags found!')
        return 'OK', 200

    ffrcore.process_new_splits(
        new_splits=new_txs,
        transaction_data=tx_data
    )

    return 'OK', 200
