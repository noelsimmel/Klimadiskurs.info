# Init file
# Used to initalize the database and create app instances

from flask import Flask, json
from flask_wtf.csrf import CSRFProtect
from klimadiskurs.config import Config
# from logging.config import dictConfig     # see below

# glossary database
with open("klimadiskurs/static/data/glossary.json", encoding="utf-8", errors="replace") as f:
    db = json.load(f)

# CSRF for form security
csrf = CSRFProtect()

def create_app(config_class=Config):
    """Mandatory app creation function. Used in run.py to create new app instances.

    Args:
        config_class (Class, optional): Flask default configurations. Defaults to Config.

    Returns:
        Flask: New Flask app.
    """

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.logger.debug("Configured app")

    csrf.init_app(app)
    app.logger.debug("Initialized CSRF")
    # set CSRF token lifespan to one day since security is not a concern
    # page has to be reloaded once the token expires to avoid 400 Bad Request
    # this is done in base.html in case a user leaves the page open that long
    app.config['WTF_CSRF_TIME_LIMIT'] = 86400

    # example on how to register blueprints
    # currently, the app is so simple it doesn't need blueprints
    # when expanding the functionality, they may be a good idea
    from klimadiskurs.app.routes import glossary
    app.register_blueprint(glossary)
    app.logger.debug("Registered blueprint: glossary")

    return app

# custom logging configuration, e.g. for changing the log level
# taken from https://flask.palletsprojects.com/en/2.0.x/logging/
# uncomment if needed, otherwise the default settings are sufficient

# dictConfig({
#     "version": 1,
#     "formatters": {"default": {
#         "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
#     }},
#     "handlers": {"wsgi": {
#         "class": "logging.StreamHandler",
#         "stream": "ext://flask.logging.wsgi_errors_stream",
#         "formatter": "default"
#     }},
#     "root": {
#         "level": "INFO",    # or "DEBUG"
#         "handlers": ["wsgi"]
#     }
# })
