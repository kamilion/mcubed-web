
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# Jinja2 imports
import jinja2
import os

# Flask-UUID imports
from flask_uuid import FlaskUUID

# Local site config imports
import app.config as config

# RethinkDB
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

# Baseplate imports
from app.baseview import BaseView

# Flask-login imports
from auth.authmodel import login_manager
from auth.authview import AuthView

# flask-defer imports
from flask_defer import FlaskDefer, after_request

########################################################################################################################
## Imports of Flask-Classful based Views
## **EDIT ME**
########################################################################################################################

# PagesView imports
from pages.pagesview import PagesView

# TicketsView imports
from tickets.ticketsview import TicketsView

# Import additional views here.

# Demo imports
from testviews.quotesview import QuotesView
from testviews.duckyview import DuckyView

########################################################################################################################
## Core Object Definition
########################################################################################################################

# Flask application configuration
flask_core = Flask(__name__)
flask_core.config.from_object(config)
flask_core.debug = config.debug
flask_core.secret_key = config.secret_key

# Register the flask-uuid extension with the core object
FlaskUUID(flask_core)

# Register the flask-defer extension with the core object
FlaskDefer(flask_core)

########################################################################################################################
## Jinja2 Template Directory override
########################################################################################################################

# Locate our root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Enumerate our 'plugins' for template folders
sub_dirs = []
for dir_name in os.listdir(root_dir):
    if os.path.isdir(os.path.join(root_dir, dir_name)):
        sub_dirs.append(os.path.join(root_dir, dir_name, 'templates'))

# Append the template directories to a list of Jinja FileSystemLoaders.
template_dirs = []
for dir_name in sub_dirs:
    template_dirs.append(jinja2.FileSystemLoader(dir_name))

# Append the default template directory too, before overriding it below.
template_dirs.append(flask_core.jinja_loader)

# Create the ChoiceLoader object from the list of FileSystemLoaders
template_loader = jinja2.ChoiceLoader(template_dirs)

# Override the template loader to search in <app_root>/*/templates/
flask_core.jinja_loader = template_loader

# Enable the Loop Controls extension
flask_core.jinja_env.add_extension('jinja2.ext.loopcontrols')

########################################################################################################################
## Registration of Flask-Login extension to the Core Object
########################################################################################################################

login_manager.init_app(flask_core)

# RethinkDB Global Methods
# These will apply to all flask-classy views first, before their own before_request.

@flask_core.before_request
def rethink_db_open():
    """
    Opens a RethinkDB Connection before every request.
    """
    try:
        g.rdb_conn = r.connect(host=config.rdb['host'], port=config.rdb['port'], auth_key=config.rdb['auth_key'])
    except RqlDriverError:
        abort(503, "Database connection could be established.")

@flask_core.after_request
def rethink_db_close(response):
    """
    Closes a RethinkDB Connection after every request.
    """
    try:
        g.rdb_conn.close()
    except AttributeError:
        pass
    return response

########################################################################################################################
## Registration of ESSENTIAL Flask-Classy based views to the Core Object
########################################################################################################################

# Baseplate registration
BaseView.register(flask_core, route_base='/')
# Authentication system registration
AuthView.register(flask_core)

########################################################################################################################
## Registration of NORMAL Flask-Classy based views to the Core Object
## **EDIT ME**
########################################################################################################################

# PagesView registration
PagesView.register(flask_core)

# TicketsView registration
TicketsView.register(flask_core)

# Register additional views here.


########################################################################################################################
## Registration of DEMONSTRATION Flask-Classy based views to the Core Object
## **EDIT ME**
########################################################################################################################

# Demo registration
QuotesView.register(flask_core)
DuckyView.register(flask_core)

