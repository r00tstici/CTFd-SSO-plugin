""" Plugin entry-point """

import json
import os

from CTFd.utils import get_app_config

from .blueprint import load_bp
from .template import update_template

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))


def load(app):
    if get_app_config("OAUTH_CREATE_BUTTON") == True:
        update_template(app)

    bp = load_bp(app)
    app.register_blueprint(bp)
