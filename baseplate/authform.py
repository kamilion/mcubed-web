from flask import flash
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms.fields import TextField, PasswordField
from wtforms.validators import Required
from auth.authmodel import User



class AuthForm(FlaskForm):
    email = TextField('email', validators=[Required()])
    password = PasswordField('password', validators=[Required()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
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


class RegisterForm(FlaskForm):
    email = TextField('email', validators=[Required()])
    password = PasswordField('password', validators=[Required()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
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

class PasswdForm(FlaskForm):
    password = PasswordField('old password', validators=[Required()])
    newpassword = PasswordField('new password', validators=[Required()])
    chkpassword = PasswordField('chk password', validators=[Required()])

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

         #  We need to get the user's id from the login session.
        user = current_user

        if user is None:
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
