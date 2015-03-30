
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

def default_pages(database):
    """
    A small function to verify RethinkDB Tables
    Runs once on database initialization.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).insert([
            {
                "meta": {
                    "active": True,
                    "object_id": 1,
                    "title": "Test Page 1",
                    "content": "test of page 1",
                    "updated_at": r.now()
                }
            }, {
                "meta": {
                    "active": True,
                    "object_id": 2,
                    "title": "Test Page 2",
                    "content": "test of page 2",
                    "updated_at": r.now()
                }
            }, {
                "meta": {
                    "active": True,
                    "object_id": 3,
                    "title": "Test Page 3",
                    "content": "test of page 3",
                    "updated_at": r.now()
                }
            }
        ]).run(conn)
        print("PAGESMODELDEFAULTS: STARTUP: Page Table defaults initialized.")
    except RqlRuntimeError:
        print("PAGESMODELDEFAULTS: STARTUP: Page Table already exists, won't reinitialize.")
    finally:
        conn.close()

def index_setup(database, index_name):
    """
    A small function to verify RethinkDB Table indexes
    Runs once on application startup.
    """
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[database].split(':')
        r.db(db[0]).table(db[1]).index_create(index_name).run(conn)
        print("PAGESMODELDEFAULTS: STARTUP: Page Table initialized.")
    except RqlRuntimeError:
        print("PAGESMODELDEFAULTS: STARTUP: Page Table exists.")
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
        index_setup(database, 'title')
        default_pages(database)
        print("PAGESMODELDEFAULTS: STARTUP: Page Table initialized.")
    except RqlRuntimeError:
        print("PAGESMODELDEFAULTS: STARTUP: Page Table exists.")
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
        print("PAGESMODELDEFAULTS: STARTUP: Page Database initialized.")
    except RqlRuntimeError:
        print("PAGESMODELDEFAULTS: STARTUP: Page Database exists.")
    finally:
        conn.close()
        table_setup(database)

