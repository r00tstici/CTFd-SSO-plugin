""" Plugin entry-point """

import json
import os

from .blueprint import load_bp

from flask_oidc import OpenIDConnect

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))

def load(app):
    app.config['OIDC_CLIENT_SECRETS'] =                 f'{PLUGIN_PATH}/sso_config.json'
    app.config['OIDC_ID_TOKEN_COOKIE_SECURE'] =         False
    app.config['OIDC_REQUIRE_VERIFIED_EMAIL'] =         False
    app.config['OIDC_USER_INFO_ENABLED'] =              True
    app.config['OIDC_OPENID_REALM'] =                   'flask-demo'
    app.config['OIDC_SCOPES'] =                         ['openid', 'email', 'profile']
    app.config['OIDC_INTROSPECTION_AUTH_METHOD'] =      'client_secret_post'

    app.db.create_all()
    oidc = OpenIDConnect(app)

    bp = load_bp(oidc)
    app.register_blueprint(bp)
