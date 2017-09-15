import importlib
import os

from flask import Flask

BASE_PATH = os.getcwd()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.FlaskConfig')

    # Auto-register Controllers
    for f in os.listdir('controllers'):
        if not f.startswith('__') and f.endswith('.py'):
            fname = f[:-3]
            controller = importlib.import_module('controllers.{}'.format(fname))
            app.register_blueprint(controller.bp)

    return app
