""" Plugin entry-point """

import json
import os

from authlib.integrations.flask_client import OAuth
from CTFd.utils import get_app_config

from .blueprint import load_bp
from .oauth import register_client
from .template import update_template

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))


def load(app):
    oauth = OAuth(app)
    register_client(oauth)

    if get_app_config("OAUTH_CREATE_BUTTON") == True:
        update_template(app)

    bp = load_bp(app, oauth)
    app.register_blueprint(bp)
