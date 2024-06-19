from flask import (
    Blueprint,
    current_app,
    jsonify
)

bp_main = Blueprint('main', __name__)


@bp_main.route('/', methods=['GET'])
def index():
    return jsonify({
        'app_name': current_app.name,
        'version': current_app.config.get('VERSION')
    }), 200
