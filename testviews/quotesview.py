
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_classful import FlaskView, route
from random import choice

# we'll make a list to hold some quotes for our app
quotes = [
    "A noble spirit embiggens the smallest man! ~ Jebediah Springfield",
    "If there is a way to do it better... find it. ~ Thomas Edison",
    "No one knows what he can do till he tries. ~ Publilius Syrus"
]

########################################################################################################################
## Class Definitions
########################################################################################################################

class QuotesView(FlaskView):
    """
    A simple demonstration view for Flask-Classful.
    """
    #route_base = '/'

    def index(self):
        return "<br>".join(quotes)

    def get(self, id):
        id = int(id)
        if id < len(quotes) - 1:
            return quotes[id]
        else:
            return "Not Found", 404

    def random(self):
        return choice(quotes)

    def crosstest(self):
        return redirect(url_for("DuckyView:get", name="Howard"))

    def ducktest(self):
        return redirect(url_for('do_duck_stuff'))

    def templatetest(self):
        return render_template('tester.html')