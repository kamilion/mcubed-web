
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Local site config imports
from app.config import smtp

# SMTP library import
import smtplib

# Email imports
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

########################################################################################################################
## Helper Functions
########################################################################################################################

def send_email(emailtarget, msg):
    try:
        mailserver = smtplib.SMTP(smtp['host'], smtp['port']) # Open a connection to the SMTP server.
    except socket.error:
        print("Something went wrong with the socket.")

    if smtp['tls']: # Then try to connect to the server and open a TLS tunnel.
        tlsresponse = mailserver.ehlo() # Ask the server what it supports, save the result.
        print('Asking server if it supports TLS:\n{}'.format(tlsresponse)) # do something better here.
        try: # to start a TLS tunnel
            mailserver.starttls() # Ask the server if it will open a TLS tunnel.
        except smtplib.SMTPException:
            print("\nServer didn't support TLS, falling back to insecure plaintext.")

    mailserver.ehlo() # Ask the server what it supports, preferably over the TLS tunnel.

    try: # to log in to the server
        mailserver.login(smtp['username'], smtp['password']) # username format for exchange: 'domain\username'
    except smtplib.SMTPAuthenticationError:
        print("Couldn't authenticate with server using username {}.".format(smtp['username']))

    try: # to send the message
        mailserver.sendmail(smtp['replyto'], emailtarget, msg) # Send the message
    except smtplib.SMTPDataError:
        print("Server refused to accept our message to {}.".format(emailtarget))

    mailserver.quit() # Disconnect from the mailserver.

def bundle_email(emailtext, emailhtml, emailsubject, emailtarget):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = emailsubject
    msg['From'] = smtp['replyto']
    msg['To'] = emailtarget

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(emailtext, 'plain')
    part2 = MIMEText(emailhtml, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the *last* part of a multipart message, 
    # (in this case the HTML message) is preferred by the client.
    msg.attach(part1)
    msg.attach(part2)

    # Return the completed message as a string.
    return msg

def compose_email_and_send(emailtext, emailhtml, emailsubject, emailtarget):
    send_email(emailtarget, bundle_email(emailtext, emailhtml, emailsubject, emailtarget).as_string())
