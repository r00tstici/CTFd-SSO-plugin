""" Plugin entry-point """

import json
import os

from .blueprint import load_bp

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))

def load(app):

    app.db.create_all()

    bp = load_bp(app)
    app.register_blueprint(bp)
