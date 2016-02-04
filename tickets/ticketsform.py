
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import flash, request, redirect
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms.fields import TextField, TextAreaField, PasswordField, HiddenField
from wtforms.validators import DataRequired
# ReCAPTCHA imports
from flask.ext.wtf.recaptcha import RecaptchaField

# urlparse imports
from urlparse import urlparse, urljoin

# Our own Tickets model
from tickets.ticketsmodel import Ticket

from app.mailer import compose_email_and_send


########################################################################################################################
## Helper Functions
########################################################################################################################

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

########################################################################################################################
## Class Definitions
########################################################################################################################

class TicketForm(RedirectForm):
    """
    A simple Ticket form.
    Will create Tickets and may provide a Ticket object, if found, to the View.
    """
    source = HiddenField('source')
    name = TextField('name', validators=[DataRequired()])
    email = TextField('email', validators=[DataRequired()])
    phone = TextField('phone', validators=[DataRequired()])
    message = TextAreaField('message', validators=[DataRequired()])
    recaptcha = RecaptchaField()

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

        ticket = Ticket.create(self.source.data, self.name.data, self.email.data, self.phone.data, self.message.data)

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
            if self.source.data=='fireeye':
              compose_email_and_send(text, html, subject, 'FireEye.TB@m-cubed.com')
            elif self.source.data=='riverbed':
              compose_email_and_send(text, html, subject, 'rb@m-cubed.com')
            else:
              compose_email_and_send(text, html, subject, 'mteam@m-cubed.com')
            return True
        else:
            return False

