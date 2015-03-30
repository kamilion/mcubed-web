
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import g

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb


########################################################################################################################
## Helper Functions
########################################################################################################################

def default_users(database):
    """
    A small function to verify RethinkDB Tables
    Runs once on database initialization.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).insert([
            {
                "active": True,
                "admin": True,
                "email": "kamilion@gmail.com",
                "identity_yubico":  "ccccccdbildi",
                "password": ""
            }, {
                "active": True,
                "admin": True,
                "email": "kyle@ospnet.org",
                "identity_yubico": "ccccccdtvhef",
                "password": ""
            }, {
                "active": True,
                "admin": True,
                "email": "dwfreed@mtu.edu",
                "identity_yubico": "ccccccbcjegt",
                "password": ""
            }, {
                "active": True,
                "admin": True,
                "email": "vinh@m-cubed.com",
                "password": "736372797074000f00000008000000016c40f41df157999531c9240dc8e08009e72f1cf05bfec7a048d6da6a586c03b728788a020abc343388ec905010e1c8721962ada1917530edebb3ad1a05b3c50e3b60fa25bba205cec724a95b73715069e4c5654992d049a8b3b3e8e6aef6a479cc355c25524f3a1949a71801cc752bbd7674afa330c8f93ad6d3ed00b951854276f40eb68d95c6ccd550cf73aa2211f2075be1b66cfcddb4f61dde19d490e12b787733b043adbf69a7e15f10701001ca"
            }, {
                "active": True,
                "admin": True,
                "email": "amitchell@m-cubed.com",
                "password": "736372797074000f0000000800000001a70736cb4d83d9365d3621a814b57d84dad76deec612a24841a4f0e29f36271c3d6a3c4c5c23a83adccae95d3e5ad01177ed13031ae1a188f314ad860621b87b967516b20549f0a4ac14dcd0f261dd12268c30a91bc33e6d9dca75cdf6bb6b14053e641e7f3678c17cb61b5a765aca6a99655a9fda74cffa5eddb22e89f595eac742d1d3832e581744716c7e9087112a5b384cf035899c9ccc1cb687042de314e6515f71b6958732fafd88ccd36aae7e"
            }
        ]).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Table defaults initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table already exists, won't reinitialize.")
    finally:
        conn.close()

def index_setup(database, index_name):
    """
    A small function to verify RethinkDB Tables
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).index_create(index_name).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Table Index initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table Index exists.")
    finally:
        conn.close()

def table_setup(database):
    """
    A small function to verify RethinkDB Tables
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        index_setup(database, 'email')
        default_users(database)
        print("AUTHMODELDEFAULTS: STARTUP: User Table initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Table exists.")
    finally:
        conn.close()

def db_setup(database):
    """
    A small function to verify RethinkDB Databases.
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db_create(db[0]).run(conn)
        print("AUTHMODELDEFAULTS: STARTUP: User Database initialized.")
    except RqlRuntimeError:
        print("AUTHMODELDEFAULTS: STARTUP: User Database exists.")
    finally:
        conn.close()
        table_setup(database)

