from flask import (
    Blueprint,
    current_app,
    request,
    jsonify
)

from ffrelay.routes.helpers import get_app_logger

bp_trans = Blueprint('transaction', __name__, url_prefix='/transaction')


@bp_trans.route('/add', methods=['GET', 'POST'])
def add_transaction():
    log = get_app_logger()
    data = request.data

    log.info('Received add transaction data:')
    log.info(data)
    # TODO: Take in new transaction
    return jsonify({
        'app_name': current_app.name,
        'version': current_app.config.get('VERSION')
    }), 200


@bp_trans.route('/update', methods=['GET', 'POST'])
def update_transaction():
    data = request.data
    # TODO: Update transaction
    return jsonify({
        'app_name': current_app.name,
        'version': current_app.config.get('VERSION')
    }), 200
