
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import g

# Flask-login imports
from flask.ext.login import LoginManager, UserMixin

# Third Party Libraries
import scrypt
import random

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb
import auth.authdefaults as authdefaults
# Run these tasks when we're first imported by uwsgi or executed.
authdefaults.db_setup('userdb')

# Hotp tokens are currently disabled due to pyotp and py3 not playing well.
# pyotp imports
#import pyotp

# yubikey imports
from yubico_client import Yubico
from yubico_client.otp import OTP
from app import config

yubico = Yubico(config.yubico_keys['client_id'], config.yubico_keys['secret_key'])

login_manager = LoginManager()

########################################################################################################################
## Login_Manager's required User Loader function
########################################################################################################################

@login_manager.user_loader
def load_user(user_uuid):
    """
    Instantiate a user object from a RethinkDB document UUID
    @param user_uuid: The RethinkDB UUID to request
    """
    if user_uuid != "None":
        try:
            return User(user_uuid)
        except NoSuchUUIDExists:
            return None


########################################################################################################################
## Utility Classes
########################################################################################################################


class NoSuchUUIDExists(Exception):
    """
    A small exception class to identify potential UUID mishaps
    """
    pass


########################################################################################################################
## User Class
########################################################################################################################


class User(UserMixin):
    """
    This class represents a user in RethinkDB.
    A User class derived from the Flask-Login UserMixin superclass.
    """
    id = None
    email = None
    password = None
    admin = None
    active = None
    auth_yubitoken = None
    # Hotp tokens are currently disabled due to pyotp and py3 not playing well.
    #auth_hotptoken = None

    def __init__(self, user_uuid):
        """
        Create a user object from a RethinkDB document
        @param user_uuid: The RethinkDB UUID to request
        """
        try:
            db = rdb['userdb'].split(':')
            results = r.db(db[0]).table(db[1]).get(user_uuid).run(g.rdb_conn)
        except RqlRuntimeError:
            print("AUTHMODEL: InitUser: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(user_uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.email = results['email']
        self.active = results['active']
        self.admin = results['admin']
        self.password = results['password']
        try:
            self.auth_yubitoken = results['identity_yubico']
        except KeyError:
            pass
        # Hotp tokens are currently disabled due to pyotp and py3 not playing well.
        #try:
        #    self.auth_hotptoken = results['identity_hotp']
        #except KeyError:
        #    pass
        print("AUTHMODEL: InitUser: {} Admin: {}".format(self.email, self.admin))

    # Overrides UserMixin
    def is_active(self):
        """
        Check if a user entry is currently an Active User
        @return: True if the User was active, or False if the operation could not complete.
        """
        return self.active

    def check_yubitoken(self, token):
        """
        Check the token of a user entry from a provided YubiCo token
        @param token: The token to check against a YubiCo OTP
        @return: True if the token was valid, or False if the operation could not complete.
        """
        if self.auth_yubitoken is not None:
            try:  # to verify the token against yubico servers
                y = yubico.verify(token)
            except:  # If it doesn't work, just return none.
                y = None
            # But if it did work, check against our stored token.
            if y and OTP(token).device_id == self.auth_yubitoken[0:12]:
                return True
        return False

    # Hotp tokens are currently disabled due to pyotp and py3 not playing well.
    #def check_hotptoken(self, token):
    #    """
    #    Check the token of a user entry from a provided HOTP token
    #    @param token: The token to check against a HOTP timestamp secret
    #    @return: True if the token was valid, or False if the operation could not complete.
    #    """
    #    if self.auth_hotptoken is not None:
    #        try:
    #            token = int(token)
    #        except ValueError:
    #            token = 0
    #        if pyotp.TOTP(self.auth_hotptoken).now() == token:
    #            return True
    #    return False

    def check_password(self, input_pass):
        """
        Check the password of a user entry from a provided input password
        @param input_pass: The password to decode the secret with
        @return: True if the password was valid, or False if the operation could not complete.
        """
        try:
            result = scrypt.decrypt(  # Decode the crypto stream
                self.password.decode('hex'),  # By pulling the hexed password from the DB
                input_pass.encode('ascii', 'ignore'),  # And passing in the password
                0.5)  # Take half a second to do this.
            print("AUTHMODEL: CheckPassword: SUCCESS InputPass: {}".format(input_pass))
            return True  # We don't check our cookie above, but it matches.
        except scrypt.error:
            print("AUTHMODEL: CheckPassword: FAILED InputPass: {}".format(input_pass))
            return False  # Because you get 'password is incorrect' if it does not.

    def change_password(self, input_pass):
        """
        Change the password of a user entry from an new password
        @param input_pass: The password to register with RethinkDB
        @return: True if the record was updated, or False if the operation could not complete.
        """
        try:
            new_password = scrypt.encrypt(
                ''.join(chr(random.randint(0, 255)) for i in range(64)),  # Store a Random Cookie
                input_pass.encode('ascii', 'ignore'),  # Assure the password is ascii.
                0.5  # How long should we take?
            ).encode('hex')  # Store the completed password as hex
            print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
            try:
                db = rdb['userdb'].split(':')
                r.db(db[0]).table(db[1]).get(self.id).update(
                    {"password": new_password}
                ).run(g.rdb_conn)
            except RqlRuntimeError:
                return False
            return True  # We don't check our cookie above, but it matches.
        except scrypt.error:
            return False  # Because you get 'password is incorrect' if it does not.

    # Convenience method
    @classmethod
    def create(cls, email, input_pass):
        """
        Create a new user entry from an email address and password
        @param email: The email address to register with RethinkDB
        @param input_pass: The password to register with RethinkDB
        @return: A User object instantiated from the requested email address, or None.
        """
        try:  # To make a crypted password
            new_password = scrypt.encrypt(
                ''.join(chr(random.randint(0, 255)) for i in range(64)),  # Store a Random Cookie
                input_pass.encode('ascii', 'ignore'),  # Assure the password is ascii.
                0.5  # How long should we take?
            ).encode('hex')  # Store the completed password as hex
            print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
        except scrypt.error:
            return None  # Because you get 'password is incorrect' if it does not.

        try:  # To make the database entry with the crypted password
            db = rdb['userdb'].split(':')
            inserted = r.db(db[0]).table(db[1]).insert(
                {"email": email, "password": new_password, "active": True, "admin": False }
            ).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return User(inserted['generated_keys'][0])  # We don't check our scrypt cookie above, but it matches.


    # Convenience method
    @classmethod
    def get_user_from_email(cls, email):
        """
        Create a user object from an email address
        @param email: The email address to request from RethinkDB
        @return: A User object instantiated from the requested email address, or None.
        """
        if email == "None":
            return None
        else:
            try:
                db = rdb['userdb'].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(
                    {'email': email}
                ).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return User(document['id'])
            except RqlRuntimeError:
                return None

    # Convenience method
    @classmethod
    def get_user_from_yubitoken(cls, yubitoken):
        """
        Create a user object from an yubikey token
        @param yubitoken: The YubiCo Identity to request from RethinkDB
        @return: A User object instantiated from the requested YubiCo Identity, or None.
        """
        if yubitoken == "None":
            return None
        else:
            try:
                db = rdb['userdb'].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(  # Make sure the yubico field is there.
                    lambda this_user: this_user.has_fields('identity_yubico')
                ).filter(  # Just in case someone stored a full token instead of identity.
                    lambda row: row['identity_yubico'].match("^{}".format(yubitoken[0:12]))
                ).pluck('id').run(g.rdb_conn)  # Return only the UUID for this record.
                for document in cursor:
                    return User(document['id'])  # Return the user object via instantiation
            except RqlRuntimeError:
                return None


    def __repr__(self):
        return '<User {} Admin: {}>'.format(self.email, self.admin)
