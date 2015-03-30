
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import flash
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms.fields import TextField, PasswordField
from wtforms.validators import DataRequired

# YubiCo import for quick identity splitting
from yubico_client.otp import OTP

# Our own User authentication model
from auth.authmodel import User


########################################################################################################################
## Class Definitions
########################################################################################################################

class AuthForm(Form):
    """
    A simple Email and Password authentication form.
    Will do user lookups and provide a User object, if found, to the View.
    """
    email = TextField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Retrieve a user object from a User class
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: A User object representing the found user, or None
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

         #  We need to find a user's id by their email address.
        user = User.get_user_from_email(self.email.data)

        if user is None:
            self.email.errors.append('Unknown Email Address')
            flash('Unknown Email Address', 'error')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            flash('Invalid password', 'error')
            return False

        self.user = user
        return True


class YubiAuthForm(Form):
    """
    A simple YubiKey authentication form.
    Will do user lookups and provide a User object, if found, to the View.
    """
    yubi_input = PasswordField('YubiKey', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Retrieve a user object from a User class using a YubiKey token
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: A User object representing the found user, or None
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

        identity = OTP(self.yubi_input.data).device_id

         #  We need to find a user's id by their Yubico Token ID.
        user = User.get_user_from_yubitoken(identity)

        if user is None:
            self.yubi_input.errors.append('Unknown Identity')
            flash('Unknown Identity', 'error')
            return False

        if not user.check_yubitoken(self.yubi_input.data):
            self.yubi_input.errors.append('Invalid Token')
            flash('Invalid Token', 'error')
            return False

        self.user = user
        return True


class RegisterForm(Form):
    """
    A simple Email and Password registration form.
    Will do user lookups and provide a User object, if found, to the View.
    """
    email = TextField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Register a new a user object via a User class helper
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: True if the User object was successfully created, or False if it was not.
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

         #  We need to find a user's id by their email address.
        user = User.get_user_from_email(self.email.data)

        if user is not None:
            self.email.errors.append('Email Address Exists')
            flash('Email Address Exists', 'error')
            return False

        user = User.create(self.email.data, self.password.data)

        if user is not None:
            self.user = user
            return True
        else:
            return False


class PasswdForm(Form):
    """
    A simple Password Change form.
    Will do user lookups and alter the User object without returning it to the View.
    """
    password = PasswordField('old password', validators=[DataRequired()])
    newpassword = PasswordField('new password', validators=[DataRequired()])
    chkpassword = PasswordField('chk password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Change the password of a user object via a User class helper
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: True if the password can be changed, or False if the operation should not continue.
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

        ## We need to get the user's id from the login session.
        user = current_user  # current_user is a proxy object.
        # We need to assign it to a local to get the reference to the real User object.

        if user is None:  # Then the user doesn't exist.
            flash('Unknown User', 'error')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid old password')
            flash('Invalid old password', 'error')
            return False

        if not self.chkpassword.data == self.newpassword.data:
            self.newpassword.errors.append('New Password pair does not match')
            flash('New Password pair does not match', 'error')
            return False

        return True
