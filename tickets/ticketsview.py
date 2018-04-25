__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

# Flask-login imports
from flask_login import current_user, login_required

# Flask-classful imports
from flask_classful import FlaskView, route

# Flask-WTF imports
from tickets.ticketsform import TicketForm

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb
# This Class uses database configuration:
cdb = 'ticketsdb'

# Pull in our local model
from tickets.ticketsmodel import Ticket

########################################################################################################################
## View Class
########################################################################################################################
class TicketsView(FlaskView):
    #decorators = [login_required]

    def index(self):
        form = TicketForm()
        form.source.data = "ContactUs"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/fireeye', endpoint='fireeye', methods=['GET'])
    def fireeye(self):
        form = TicketForm()
        form.source.data = "fireeye"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/fireeye-eval', endpoint='fireeye_eval', methods=['GET'])
    def fireeye_eval(self):
        form = TicketForm()
        form.source.data = "fireeye-eval"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/riverbed', endpoint='riverbed', methods=['GET'])
    def riverbed(self):
        form = TicketForm()
        form.source.data = "riverbed"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/riverbed-weee', endpoint='riverbed_weee', methods=['GET'])
    def riverbed_weee(self):
        form = TicketForm()
        form.source.data = "riverbed-weee"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/aurora', endpoint='aurora', methods=['GET'])
    def aurora(self):
        form = TicketForm()
        form.source.data = "aurora"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/equitrac', endpoint='equitrac', methods=['GET'])
    def equitrac(self):
        form = TicketForm()
        form.source.data = "equitrac"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/inada', endpoint='inada', methods=['GET'])
    def inada(self):
        form = TicketForm()
        form.source.data = "inada"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/windriver', endpoint='windriver', methods=['GET'])
    def windriver(self):
        form = TicketForm()
        form.source.data = "windriver"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/wonderworkshop', endpoint='wonderworkshop', methods=['GET'])
    def wonderworkshop(self):
        form = TicketForm()
        form.source.data = "wonderworkshop"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('/nuance', endpoint='nuance', methods=['GET'])
    def nuance(self):
        form = TicketForm()
        form.source.data = "nuance"
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @route('do_ticket', methods=['POST'])
    def do_ticket(self):
        """
        Processing of a User Submitted Ticket Flask-WTF form
        @return: A Jinja2 Template containing a Ticket form, or a redirect to the index or next page.
        """
        form = TicketForm()
        if form.validate_on_submit():
            flash('Message Sent.', 'success')
            return redirect(request.args.get('next') or url_for('TicketsView:index'))
        return render_template('tickets/ticketform-{}.html'.format(form.source.data), form=form)

    @login_required
    def admin(self):
        """
        Admin of User Submitted Ticket Flask-WTF forms.
        The parenthesis around ~ is required to evaluate it on the far end.
        see https://www.rethinkdb.com/api/python/has_fields/
        and https://www.rethinkdb.com/api/python/not/
        @return: A Jinja2 Template containing a Ticket list, or 404.
        """
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1])
            .filter( 
                 ( ~r.row.has_fields( { 'meta': { 'archived': True } } ) )
            ).order_by(
                 r.desc(lambda date: date['meta']['updated_at'])
            ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            return render_template('tickets/ticketslist.html', results=selection)
        else:
            return "Not Found", 404

    @login_required
    def archived(self):
        """
        Archive of all User Submitted Ticket Flask-WTF forms.
        @return: A Jinja2 Template containing a Ticket list, or 404.
        """
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1])
            .order_by(
                 r.desc(lambda date: date['meta']['updated_at'])
            ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            return render_template('tickets/ticketslist.html', results=selection)
        else:
            return "Not Found", 404

    @login_required
    def get(self, uuid):
        """
        Admin of User Submitted Ticket Flask-WTF forms.
        Returns a single ticket.
        @return: A Jinja2 Template containing a Ticket, or 404.
        """
        db = rdb[cdb].split(':')
        selection = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if selection is not None:
            #print(selection)
            return render_template('tickets/ticket.html', results=selection)
        else:
            return "Not Found", 404

    @login_required
    def archive(self, uuid):
        """
        Archival of User Submitted Ticket Flask-WTF forms.
        @return: A Jinja2 Template containing a Ticket, or 404.
        """
        if Ticket(uuid).mark_as_archived():
          db = rdb[cdb].split(':')
          selection = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
          if selection is not None:
              #print(selection)
              #return render_template('tickets/ticket.html', results=selection)
              return redirect(url_for('TicketsView:admin'))
          else:
              return "Not Found", 404
        else:
            return "Not Found", 404
