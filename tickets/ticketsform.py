
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import flash
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms.fields import TextField, TextAreaField, PasswordField
from wtforms.validators import DataRequired

# Our own Tickets model
from tickets.ticketsmodel import Ticket

from app.mailer import compose_email_and_send

########################################################################################################################
## Class Definitions
########################################################################################################################

class TicketForm(Form):
    """
    A simple Ticket form.
    Will create Tickets and may provide a Ticket object, if found, to the View.
    """
    name = TextField('name', validators=[DataRequired()])
    email = TextField('email', validators=[DataRequired()])
    phone = TextField('phone', validators=[DataRequired()])
    message = TextAreaField('message', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Register a new a Ticket object via a Ticket class helper
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.ticket = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: True if the Ticket object was successfully created, or False if it was not.
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

        ticket = Ticket.create(self.name.data, self.email.data, self.phone.data, self.message.data)

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nA new ticket has been created by {}.\nHere is the link:\nhttp://www.m-cubed.com/tickets/{}".format(ticket.name, ticket.id)
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               A new ticket has been created by {}.<br>
               Here is the <a href="http://www.m-cubed.com/tickets/{}">link</a> to the ticket.
            </p>
          </body>
        </html>
        """.format(ticket.name, ticket.id)
        subject = "[Ticket] A new ticket has been created by {}.".format(ticket.name)

        if ticket is not None:
            compose_email_and_send(text, html, subject, 'mteam@m-cubed.com')
            return True
        else:
            return False

