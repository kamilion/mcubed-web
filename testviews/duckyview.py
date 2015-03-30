
########################################################################################################################
## Imports
########################################################################################################################

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.login import login_required, current_user
from flask.ext.classy import FlaskView, route


########################################################################################################################
## Class Definitions
########################################################################################################################

class DuckyView(FlaskView):
    """
    A simple authentication-required view for Flask-Classy.
    Relies on flask-login to provide a User object, if found, to the View.
    """
    decorators = [ login_required ]

    def index(self):
        return "Duckies for {}!".format(current_user.email)

    def get(self, name):
        return "Hold on, {} getting Duck named {}".format(current_user.id, name)

    @route('/do_duck_stuff', endpoint='do_duck_stuff')
    def post(self):
        return "Um... Quack?"