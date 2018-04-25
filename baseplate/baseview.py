from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_classful import FlaskView, route

class BaseView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('baseplate/index.html')

