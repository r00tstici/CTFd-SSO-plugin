""" Plugin entry-point """

import json
import os

from .blueprint import load_bp

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))

def load(app):

    app.config['SERVER_NAME']                   = ''
    app.config['OAUTH_AUTHORIZATION_ENDPOINT']  = ''
    app.config['OAUTH_CLIENT_ID']               = ''
    app.config['OAUTH_TOKEN_ENDPOINT']          = ''
    app.config['OAUTH_API_ENDPOINT']            = ''
    app.config['OAUTH_CLIENT_SECRET']           = ''

    app.db.create_all()

    bp = load_bp(app)
    app.register_blueprint(bp)
