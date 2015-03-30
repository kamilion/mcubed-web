
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# Flask-login imports
from flask.ext.login import login_user, logout_user, current_user, login_required

# Flask-classy imports
from flask.ext.classy import FlaskView, route

from app.config import allow_new_users

########################################################################################################################
## View Class
########################################################################################################################
class BaseView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('baseplate/index.html', registration=allow_new_users)

    def home(self):
        return render_template('baseplate/home.html')

    def privacy(self):
        return render_template('baseplate/privacy.html')

    def about(self):
        return render_template('baseplate/about.html')

    def contact(self):
        return render_template('baseplate/contact.html')

