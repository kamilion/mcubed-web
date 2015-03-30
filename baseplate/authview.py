# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# Flask-login imports
from flask.ext.login import login_user, logout_user, current_user, login_required

# Flask-classy imports
from flask.ext.classy import FlaskView, route

# Flask-WTF imports
from authform import AuthForm, RegisterForm, PasswdForm

# View class

class AuthView(FlaskView):
    def index(self):
        form = AuthForm()
        return render_template('auth/login.html', form=form)

    def post(self):
        form = AuthForm()
        if form.validate_on_submit():
            login_user(form.user, remember=True)
            flash('logged in', 'success')
            return redirect(request.args.get("next") or url_for("BaseView:index"))
        return render_template('auth/login.html', form=form)

    def logout(self):
        logout_user()
        return redirect(url_for('BaseView:index'))

    def new_user(self):
        form = RegisterForm()
        return render_template('auth/register.html', form=form)

    @route('do_register', methods=['POST'])
    def do_register(self):
        form = RegisterForm()
        if form.validate_on_submit():
            login_user(form.user, remember=True)
            flash('registered and logged in', 'success')
            return redirect(request.args.get("next") or url_for("BaseView:index"))
        return render_template('auth/register.html', form=form)

    def passwd(self):
        form = PasswdForm()
        return render_template('auth/passwd.html', form=form)

    @route('do_passwd', methods=['POST'])
    def do_passwd(self):
        form = PasswdForm()
        if form.validate_on_submit():
            # Change password here
            current_user.change_password(form.newpassword.data)
            flash('password changed', 'success')
            return redirect(request.args.get("next") or url_for("BaseView:index"))
        return render_template('auth/passwd.html', form=form)
