
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import flash, request, redirect
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.fields import TextField, TextAreaField, PasswordField, HiddenField
from wtforms.validators import DataRequired
# ReCAPTCHA imports
from flask_wtf.recaptcha import RecaptchaField

# urlparse imports
from urlparse import urlparse, urljoin

# bleach imports
import bleach

# flask-defer imports
from flask_defer import FlaskDefer, after_request

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

class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
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
    phone = TextField('phone')
    message = TextAreaField('message', validators=[DataRequired()])
    recaptcha = RecaptchaField()

    def __init__(self, *args, **kwargs):
        """
        Register a new a Ticket object via a Ticket class helper
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        FlaskForm.__init__(self, *args, **kwargs)
        self.ticket = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: True if the Ticket object was successfully created, or False if it was not.
        """
        rv = FlaskForm.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

        ticket = Ticket.create(self.source.data, self.name.data, self.email.data, self.phone.data, self.message.data)

        if ticket is not None:
            after_request(self.send_notification, ticket)
            return True
        else:
            return False


    def send_notification(self, ticket):
        safe_name = bleach.clean(ticket.name)
        safe_email = bleach.clean(ticket.email)        
        safe_phone = bleach.clean(ticket.phone)
        safe_text = bleach.clean(ticket.message)

        # Create the body of the message (a plain-text and an HTML version).
        text = u"""\
A new {} ticket has been created. Here is the link:
http://www.m-cubed.com/tickets/{} 

Date/Time: {}
Name: {}
Email: {}
Phone: {}
Message: {}

        """.format(ticket.source, ticket.id, ticket.updated_at, safe_name, safe_email, safe_phone, safe_text)
        html = u"""\
        <html>
          <head></head>
          <body>
            <p>A new {} ticket has been created. Here is the <a href="http://www.m-cubed.com/tickets/{}">link</a> to the ticket.<br><br>
               Date/Time: {}<br><br>
               Name: {}<br><br>
               Email: {}<br><br>
               Phone: {}<br><br>
               Message: {}<br><br>
            </p>
          </body>
        </html>
        """.format(ticket.source, ticket.id, ticket.updated_at, safe_name, safe_email, safe_phone, safe_text)
        subject = u"[Ticket] A new {} ticket has been created by {} ({}).".format(ticket.source, safe_name, safe_email)

        if ticket is not None:
            if self.source.data=='fireeye':
              compose_email_and_send(text, html, subject, 'FireEye.TB@m-cubed.com')
            elif self.source.data=='fireeye-eval':
              compose_email_and_send(text, html, subject, 'FireEye.eval@m-cubed.com')
            elif self.source.data=='riverbed':
              compose_email_and_send(text, html, subject, 'rb@m-cubed.com')
            elif self.source.data=='riverbed-weee':
              compose_email_and_send(text, html, subject, 'rb.weee@m-cubed.com')
            else:
              compose_email_and_send(text, html, subject, 'mtickets@m-cubed.com')


