
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# Flask-login imports
from flask.ext.login import login_user, logout_user, current_user, login_required

# Flask-classy imports
from flask.ext.classy import FlaskView, route

# Flask-WTF imports
from auth.authform import AuthForm, RegisterForm, PasswdForm, YubiAuthForm

from app.config import allow_new_users

########################################################################################################################
## View Class
########################################################################################################################
class AuthView(FlaskView):
    """
    A simple authentication view for Flask-Classy.
    Relies on flask-wtf forms to do user lookups and provide a User object, if found, to the View.
    """
    def index(self):
        """
        Display of a Flask-Login compatible Flask-WTF form for standard Email + Passwords.
        @return: A Jinja2 Template containing a login form
        """
        form = AuthForm()
        return render_template('auth/login.html', form=form)

    def post(self):
        """
        Processing of a Flask-Login compatible Flask-WTF form
        @return: A Jinja2 Template containing a login form, or a redirect to the index or next page.
        """
        form = AuthForm()
        if form.validate_on_submit():
            login_user(form.user, remember=True)
            flash('logged in', 'success')
            return redirect(request.args.get('next') or url_for('BaseView:index'))
        return render_template('auth/login.html', form=form)

    def logout(self):
        """
        Processing of a Flask-Login compatible Logout method
        @return: A redirect to the index page.
        """
        logout_user()
        return redirect(url_for('BaseView:index'))

    def no_register(self):
        """
        Displays a message preventing registering a new account.
        @return: A Jinja2 Template containing a a static error message
        """
        return render_template('auth/no_register.html')

    #@login_required
    def new_user(self):
        """
        Display of a Flask-Login compatible Flask-WTF form for registering a new account.
        @return: A Jinja2 Template containing a registration form, or if registration is disabled, a static message.
        """
        if not allow_new_users:
            return render_template('auth/no_register.html')
        else:
            form = RegisterForm()
            return render_template('auth/register.html', form=form)

    @route('do_register', methods=['POST'])
    #@login_required
    def do_register(self):
        """
        Processing of a Flask-Login compatible Flask-WTF form
        @return: A Jinja2 Template containing a registration form, or a redirect to the index or next page.
        """
        if not allow_new_users:
            return render_template('auth/no_register.html')
        else:
            form = RegisterForm()
            if form.validate_on_submit():
                login_user(form.user, remember=True)
                flash('registered and logged in', 'success')
                return redirect(request.args.get('next') or url_for('BaseView:index'))
            return render_template('auth/register.html', form=form)

    def yubikey(self):
        """
        Display of a Flask-Login compatible Flask-WTF form for YubiKey Authentication.
        @return: A Jinja2 Template containing a form with a single YubiKey field
        """
        form = YubiAuthForm()
        return render_template('auth/yubikey.html', form=form)

    @route('do_yubikey', methods=['POST'])
    def do_yubikey(self):
        """
        Processing of a Flask-Login compatible Flask-WTF form for YubiKey Authentication.
        @return: A Jinja2 Template containing a YubiKey login form, or a redirect to the index or next page.
        """
        form = YubiAuthForm()
        if form.validate_on_submit():
            login_user(form.user, remember=True)
            flash('logged in', 'success')
            return redirect(request.args.get('next') or url_for('BaseView:index'))
        return render_template('auth/yubikey.html', form=form)

    @login_required
    def passwd(self):
        """
        Display of a Flask-Login compatible Flask-WTF form for Changing Passwords.
        @return: A Jinja2 Template containing a passwd form
        """
        form = PasswdForm()
        return render_template('auth/passwd.html', form=form)

    # Route decorators always come first.
    @route('do_passwd', methods=['POST'])
    @login_required
    def do_passwd(self):
        """
        Processing of a Flask-Login compatible Flask-WTF form for Changing Passwords.
        @return: A Jinja2 Template containing a passwd form, or a redirect to the index or next page.
        """
        form = PasswdForm()
        if form.validate_on_submit():
            # Change password here
            current_user.change_password(form.newpassword.data)
            flash('password changed', 'success')
            return redirect(request.args.get('next') or url_for('BaseView:index'))
        return render_template('auth/passwd.html', form=form)
