from flask import g

# Flask-login imports
from flask_login import LoginManager, UserMixin

# Third Party Libraries
import scrypt
import random

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rethink_host, rethink_port, rethink_userdb, rethink_usertable


# db setup; only runs once
def db_setup():
    conn = r.connect(host=rethink_host, port=rethink_port)
    try:
        r.db_create(rethink_userdb).run(conn)
        print("AUTHMODEL: STARTUP: User Database initialized.")
    except RqlRuntimeError:
        print("AUTHMODEL: STARTUP: User Database exists.")
    finally:
        conn.close()


# table setup; only runs once
def table_setup():
    conn = r.connect(host=rethink_host, port=rethink_port)
    try:
        r.db(rethink_userdb).table_create(rethink_usertable).run(conn)
        r.db(rethink_userdb).table(rethink_usertable).index_create('email').run(conn)
        print("AUTHMODEL: STARTUP: User Table initialized.")
    except RqlRuntimeError:
        print("AUTHMODEL: STARTUP: User Table exists.")
    finally:
        conn.close()

# Run these tasks when we're first imported by uwsgi or executed.
db_setup()
table_setup()

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_uuid):
    if user_uuid != "None":
        try:
            return User(user_uuid)
        except NoSuchUUIDExists:
            return None


class NoSuchUUIDExists(Exception):
    pass


# This class represents a user in RethinkDB.
class User(UserMixin):
    id = None
    email = None
    password = None
    admin = None
    active = None

    def __init__(self, user_uuid):
        """
        Create a user object from a RethinkDB document
        @param user_uuid: The RethinkDB UUID to request
        """
        try:
            results = r.db(rethink_userdb).table(rethink_usertable).get(user_uuid).run(g.rdb_conn)
        except RqlRuntimeError:
            print("AUTHMODEL: InitUser: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(user_uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.email = results['email']
        self.active = results['active']
        self.admin = results['admin']
        self.password = results['password']
        print("AUTHMODEL: InitUser: {} Admin: {}".format(self.email, self.admin))

    # Overrides UserMixin
    def is_active(self):
        return self.active

    def check_password(self, input_pass):
        try:
            result = scrypt.decrypt(self.password.decode('hex'), input_pass.encode('ascii', 'ignore'), 0.5)
            print("AUTHMODEL: CheckPassword: SUCCESS InputPass: {}".format(input_pass))
            return True  # We don't check our cookie above, but it matches.
        except scrypt.error:
            print("AUTHMODEL: CheckPassword: FAILED InputPass: {}".format(input_pass))
            return False  # Because you get 'password is incorrect' if it does not.

    def change_password(self, input_pass):
        try:
            newpassword = scrypt.encrypt(''.join(chr(random.randint(0, 255)) for i in range(64)),  # Make Cookie
                                       input_pass.encode('ascii', 'ignore'), 0.5).encode('hex')
            print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
            try:
                r.db(rethink_userdb).table(rethink_usertable).get(self.id).update({"password": newpassword}).run(g.rdb_conn)
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
            newpassword = scrypt.encrypt(''.join(chr(random.randint(0, 255)) for i in range(64)),  # Make Cookie
                                       input_pass.encode('ascii', 'ignore'), 0.5).encode('hex')
            print("AUTHMODEL: SetNewPassword: InputPass: {}".format(input_pass))
        except scrypt.error:
            return None  # Because you get 'password is incorrect' if it does not.

        try:  # To make the database entry with the crypted password
            inserted = r.db(rethink_userdb).table(rethink_usertable).insert({"email": email, "password": newpassword, "active": True, "admin": False }).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return User(inserted['generated_keys'][0])  # We don't check our cookie above, but it matches.


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
                cursor = r.db(rethink_userdb).table(rethink_usertable).filter({'email': email}).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return User(document['id'])
            except RqlRuntimeError:
                return None

    def __repr__(self):
        return '<User {} Admin: {}>'.format(self.email, self.admin)
