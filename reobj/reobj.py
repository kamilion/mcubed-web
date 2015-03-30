__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# We should do logging, right?
import logging

# Flask imports
#from flask import g

# Rethink imports
import rethinkdb as r

# Pull in all the classes and methods from rethinkdb.* except for "object"
from rethinkdb.net import connect, Connection, Cursor
from rethinkdb.query import js, http, json, args, error, random, do, row, table, db, db_create, db_drop, db_list, table_create, table_drop, table_list, branch, asc, desc, eq, ne, le, ge, lt, gt, any, all, add, sub, mul, div, mod, type_of, info, time, monday, tuesday, wednesday, thursday, friday, saturday, sunday, january, february, march, april, may, june, july, august, september, october, november, december, iso8601, epoch_time, now, literal, make_timezone, and_, or_, not_
from rethinkdb.errors import RqlError, RqlClientError, RqlCompileError, RqlRuntimeError, RqlDriverError
from rethinkdb.ast import expr, RqlQuery
import rethinkdb.docs

# Rethink configuration -- Commented out, see below in the connection pool.
#from app.config import rdb
# This Class currently uses the following database configuration:
rdb = {
    'host': 'localhost',
    'port': 28015,
    'auth_key': '158bcmcubed' #,
#    'userdb': 'kaizen_auth:users',
#    'ticketsdb': 'kaizen:tickets',
#    'pagedb': 'kaizen:pages'
# These are commented out to avoid breaking **rdb in the connection pool.
}

# Import regex support
import re

# Threading for Connection Pool
# Is this even needed?
import threading
lock = threading.Lock()

# Connection Pool Imports
import Queue
from contextlib import contextmanager

########################################################################################################################
## Utility Classes
########################################################################################################################

#  I don't like this idea any more. Defining my own exceptions seems spazzy.
#class NoSuchUUIDExists(Exception):
#    pass

class ReOBJConnPool(object):
    """ 
    ReOBJConnPool: Manage a simple pool of connections to RethinkDB
    """
    # Private attributes
    _idle_connections = Queue.Queue()
    _active_connections = 0
    _maximum_connections = 5

    @contextmanager
    def get(self):
        if self._idle_connections.empty() and self._active_connections < self._maximum_connections:
            #connection = connect(**rdb)  # Will this work? Nope! Broke when I pulled kaizen-style app.config from flask in.
            connection = connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
        else:
            connection = self._idle_connections.get()
        self._active_connections += 1
        yield connection
        self._idle_connections.put(connection)
        self._active_connections -= 1

re_pool = ReOBJConnPool()

########################################################################################################################
## Helper Functions
########################################################################################################################

# None currently, all moved into respective classes.
# RIP Standalone DB creation functions, you're in a better place now.

########################################################################################################################
## ReOBJ Class
########################################################################################################################

class ReOBJ(object):
    """
    ReOBJ: a mapping layer translating RethinkDB nested JSON arrays into Python objects.
    
    Given a database, table, and document UUID, ReOBJ will instantiate an object with attributes matching the document's.
    This is dependant on your tables relying on RethinkDB's primary key default of 'id' being a UUID.
    Updating the ReOBJ's attributes will update meta['modified_at'] and perform a RethinkDB Upsert on the document.
    See the example _subclasses in reobj.py to discover how to look up objects by a different field or index.
    
    Since RethinkDB 1.15 queries are now 'lazy' about loading, The 'meta' field is given special meaning as an array meant
     to be Plucked during list-queries describing the document's contents, status, timestamps, locking information, ACLs,
     relations, ownership, etc, without actually loading the (possibly very large) contents of the actual document itself.
    It's probably not a good idea to use the 'meta' array to store large amounts of data such as icons or images.
    On a side note, it's perfectly acceptable to have a document containing only the meta field.
    """
    
    # Once connected to the cluster, this describes the database name and table name to utilize.
    # Note that RethinkDB _only_ allows underscores and alphanumerics in database and table names.
    # The format is "database_name:table_name".
    db_table = "test:test"  # We'll use the RethinkDB defaults for now so you can have fun in REPLs.
    
    # This array holds any fields that should always exist for this class.
    required_fields = []
    
    # This variable lets us know __init__ has finished and our __setattr__ can do it's job.
    #_reobj_initcomplete = False
    
    @classmethod
    def _get_conn(cls):  # Get a connection somehow.
        # return g.rdb_conn  # Get the connection from flask's global g object. (kaizen-deprecated)
        # TODO: When we move the connection pool out of the main classfile, we'll have to revisit this.
        return re_pool.get()  # For now, just use the global to grab one from the pool.
    
    @classmethod
    def _db_setup(cls):
        """
        Create a new database matching this class's configuration
        """
        db = self.db_table.split(':') # Split the database name and table name
        try:
            with cls._get_conn() as conn:
                r.db_create(db[0]).run(conn)
            print("ReOBJ:db_setup: {} Database initialized.".format(db[0]))
        except RqlRuntimeError:
            print("ReOBJ:db_setup: {} Database exists.".format(db[0]))
    
    @classmethod
    def _table_setup(cls):
        """
        Create a new table matching this class's configuration
        """
        db = self.db_table.split(':') # Split the database name and table name
        try:
            with cls._get_conn() as conn:
                r.db(db[0]).table_create(db[1]).run(conn)
                #r.db(db[0]).table(db[1]).index_create('updated_at').run(conn)
            print("ReOBJ:table_setup: {} Table initialized in {} Database.".format(db[1], db[0]))
        except RqlRuntimeError:
            print("ReOBJ:table_setup: {} Table exists in {} Database.".format(db[1], db[0]))
    
    @classmethod
    def create(cls, meta, **properties):
        """
        Create a new ReOBJ object, insert it into the database, then retrieve it and return it, ready for use.
        If necessary, you may retrieve it's UUID from the object directly from it's member attribute 'id'.
        @param meta: The meta data to store
        @param **properties: The properties to store, if any (meta data only?)
        @return: A ReOBJ instantiated from the supplied data or None.
        """
        if meta is None: # Check to see if we were passed any meta data.
            meta = {} # We were not passed any meta data, so create an empty array to hold meta data.
        meta.update({'created_at': r.now(), 'updated_at': r.now()})  # Update the timestamps.
        new_document = { 'meta': meta } # Create an array containing the meta data array.
        new_document.update(properties) # Append the properties to the array.
        try:  # To insert the new_document into the database table.
            db = self.db_table.split(':') # Split the database name and table name
            with cls._get_conn() as conn:
                inserted = r.db(db[0]).table(db[1]).insert(new_document).run(conn)#(g.rdb_conn)
        except RqlRuntimeError:  # We failed to insert the document for some reason.
            print("ReOBJ:create: Failed to insert document with meta data: {}".format(meta))
            return None  # Just tell our caller nothing was inserted, I suppose.
        new_uuid = inserted['generated_keys'][0]  # The insert was successful
        print("ReOBJ:create: {} was created with meta data: {}".format(new_uuid, meta))
        return cls(new_uuid) # Lookup and return a new object of our subclass.

    def populate_required_old(self, obj_fields):
        """
        Populate required fields in a new ReOBJ object.
        """
        # You could modify this a bit to allow required_fields to have
        # keys like "meta.name" etc, then split on periods or something. -- deontologician
        #for required_field in self.required_fields:
        #    if required_field not in results['meta']:
        #        results['meta'][required_field] = "No" + required_field.capitalize()

        # Trying to do so has resulted in the following mess:
        for required_field in self.required_fields:
            if "." not in required_field:  # This has no inner key.
                if required_field not in results: # If the key doesn't exist
                    results[required_field] = "No " + required_field.capitalize()  # Populate it with a dummy value.
            else: # We have one or more levels of fields to traverse. TODO: Handle more than a single level.
                field = required_field.split('.')  # Now we have field[0] and field[1] and maybe field[2]
                if field[0] not in obj_fields:  # If the outer key isn't available, we need to create it.
                    obj_fields[field[0]] = {} # This is now an empty array.
                if field[0][field[1]] not in obj_fields:  # If the inner key isn't available, we need to create it.
                    obj_fields[field[0]][field[1]] = "No " + field[1].capitalize()

    def populate_required(self, document):
        # iterative approach
        for field in self.required_fields:
            path = field.split('.')
            final_section = path[-1]
            subdocument = document
            for section in path:
                if section != final_section:
                    subdocument = subdocument.setdefault(section, {})
                else:
                    subdocument.setdefault(section, 'No ' + section.capitalize())

    # recursive approach (equivalent to above)
    def check_defaults(field, subdocument):
            if '.' in field:
                section, rest = field.split('.', 1)
                check_defaults(rest, subdocument.setdefault(section, {}))
            else:
                subdocument.setdefault(section, "No " + section.capitalize())
        for required_field in self.required_fields:
            check_defaults(required_field, document)

    def __init__(self, uuid):
        """
        Retrieve a ReOBJ object by looking up it's UUID.
        @return: A ReOBJ instantiated from the supplied UUID or None.
        """
        db = self.db_table.split(':')
        try:
            with self._get_conn() as conn:
                results = r.db(db[0]).table(db[1]).get(uuid).run(conn) #(g.rdb_conn)
        except RqlRuntimeError:
            print("ReOBJ:__init_: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))
        
        self.populate_required(results)
        
        for field, value in results.iteritems():  # Iterate over the fields we got from rethink
            super(ReOBJ, self).__setattr__(field, value)  # Set identical object attributes to what we received.
        
        #self._reobj_initcomplete = True  # __init__ has done it's business, let __setattr__ work.

    
    def __setattr__(self, item, value):
        """
        Sets an attribute on a ReOBJ object.
        """
        db = self.db_table.split(':')
        try:
            with self._get_conn() as conn:
                results = r.db(db[0]).table(db[1]).get(self.id).update({ item: value }).run(conn) #(g.rdb_conn)
        except RqlRuntimeError:
            print("ReOBJ:__init_: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))
        # TODO: Something in the python docs about writing to an instance dictionary or something with base class method?
        # https://docs.python.org/2/reference/datamodel.html#object.__setattr__  Does not make a whole lot of sense to me.

        
# Some example classes to demonstrate proper syntax.
# Because of their _ prefix, they will not be included in an import * from ReOBJ.
class _User(ReOBJ):
    db_table = 'auth:users'
    required_fields = ['username', 'email']
    
class _Ticket(ReOBJ):
    db_table = 'support:tickets'
    required_fields = ['meta.email', 'meta.phone', 'meta.name', 'message']

class _Page(ReOBJ):
    db_table = 'web_site:pages'
    required_fields = ['meta.template', 'content']
