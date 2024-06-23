import copy

from flask import (
    Blueprint,
    current_app,
    make_response,
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
    triggered_tx_id = data['content']['id']
    if triggered_tx_id in ffrcore.new_original_txs:
        # Transaction already handled - skip
        log.info(f'Skipping handling - already worked on original tx id: {triggered_tx_id}')
        return 'OK', 200
    elif triggered_tx_id in ffrcore.new_prop_txs:
        log.info(f'Skipping handling - already worked on proportion tx id: {triggered_tx_id}')
        return 'OK', 200

    new_txs = ffrcore.handle_incoming_transaction_data(data=data)
    for tx in new_txs:
        log.info('Creating new transaction...')
        new_tx_resp = ffrcore.new_single_transaction(**tx.get('new_tx'))
        new_tx_id = new_tx_resp.json()['data']['id']
        ffrcore.new_prop_txs.add(new_tx_id)

        log.info('Updating original transaction')
        org_tx_data = copy.deepcopy(data['content'])
        org_notes = org_tx_data['transactions'][tx['org_tx']['index']]['notes']
        tx_note = f'Prop tx: {ffrcore.base_url}/transactions/show/{new_tx_id}'
        if org_notes is None:
            org_notes = tx_note
        else:
            org_notes += f'\n{tx_note}'
        org_tx_data['transactions'][tx['org_tx']['index']]['notes'] = org_notes

        log.info('Sending transaction update.')
        ffrcore.update_transaction(data=org_tx_data)
    return 'OK', 200


@bp_trans.route('/update', methods=['GET', 'POST'])
def update_transaction():
    data = request.data
    # TODO: Update transaction
    return jsonify({
        'app_name': current_app.name,
        'version': current_app.config.get('VERSION')
    }), 200
