
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import g

# Rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# Rethink configuration
from app.config import rdb
# This Class uses database configuration:
cdb = 'ticketsdb'

# Import regex support
import re

########################################################################################################################
## Helper Functions
########################################################################################################################

# db setup; only runs once
def db_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[cdb].split(':')
        r.db_create(db[0]).run(conn)
        print("TICKETSMODEL: STARTUP: Tickets Database initialized.")
    except RqlRuntimeError:
        print("TICKETSMODEL: STARTUP: Tickets Database exists.")
    finally:
        conn.close()


# table setup; only runs once
def table_setup():
    conn = r.connect(host=rdb['host'], port=rdb['port'], auth_key=rdb['auth_key'])
    try:
        db = rdb[cdb].split(':')
        r.db(db[0]).table_create(db[1]).run(conn)
        #r.db(db[0]).table(db[1]).index_create('updated_at').run(conn)
        print("TICKETSMODEL: STARTUP: Tickets Table initialized.")
    except RqlRuntimeError:
        print("TICKETSMODEL: STARTUP: Tickets Table exists.")
    finally:
        conn.close()

# Run these tasks when we're first imported by uwsgi or executed.
db_setup()
table_setup()

########################################################################################################################
## Utility Classes
########################################################################################################################

class NoSuchUUIDExists(Exception):
    pass


########################################################################################################################
## Tickets Class
########################################################################################################################

# This class represents a Ticket in RethinkDB.
class Ticket():
    id = None
    updated_at = None
    results = {}

    def __init__(self, uuid):
        """
        Create an object from a RethinkDB document
        @param uuid: The RethinkDB UUID to request
        """
        try:
            db = rdb[cdb].split(':')
            results = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        except RqlRuntimeError:
            print(u"TICKETSMODEL: InitTicket: Critical Failure: Saving Throw Failed! while looking up UUID: {}".format(uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.updated_at = results['meta']['updated_at']


        # These fields may potentially be missing.
        try:
            self.source = results['meta']['source']
        except KeyError:
            self.source = "Unknown Source"

        try:
            self.name = results['meta']['name']
        except KeyError:
            self.name = "No Name"

        try:
            self.email = results['meta']['email']
        except KeyError:
            self.email = "No Email"

        try:
            self.phone = results['meta']['phone']
        except KeyError:
            self.phone = "No Phone Number"

        try:
            self.archived = results['meta']['archived']
        except KeyError:
            self.archived = False

        try:
            self.message = results['message']
        except KeyError:
            self.message = "Empty Message"

        try:
            self.results = results
        except KeyError:
            self.results = {}

        #print(
        #    u"TICKETSMODEL: Ticket_ID: {} Source: {} Name: {} Phone: {} Email: {} Archived: {}".format(
        #    self.id, self.source, self.name, self.phone, self.email, self.archived ))
        print(
            u"TICKETSMODEL: Ticket_ID: {} Source: {} Archived: {}".format(
            self.id, self.source, self.archived ))


    # Convenience method
    @classmethod
    def create(cls, source, name, email, phone, message):
        """
        Create a new Ticket entry.
        @return: A Ticket object instantiated from the supplied data or None.
        """
        try:  # To make the database entry with the user_id
            db = rdb[cdb].split(':')
            inserted = r.db(db[0]).table(db[1]).insert({'meta': {
                "source": source,
                "name": name,
                "email": email,
                "phone": phone,
                "updated_at": r.now()
                }, "message": message
            }).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return Ticket(inserted['generated_keys'][0])

    def mark_as_archived(self):
        """
        Mark a Ticket entry as archived
        @return: True if the ticket was updated or None.
        """
        try:  # To update the database entry with the uuid given
            db = rdb[cdb].split(':')
            db_request = r.db(db[0]).table(db[1]).get(self.id).update({'meta': {
                "archived": r.now()
                }
            }).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return True


    # Convenience method
    @classmethod
    def get_ticket_from_email(cls, email):
        """
        Create a Ticket object from an email address
        @param email: The email address to request from RethinkDB
        @return: A Ticket object instantiated from the requested email address, or None.
        """
        if email == "None":
            return None
        else:
            try:
                db = rdb[cdb].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(
                    r.row['meta']['email'] == email
                ).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return Ticket(document['id'])
            except RqlRuntimeError:
                return None

    # Convenience method
    @classmethod
    def get_ticket_from_phone(cls, phone):
        """
        Create a Ticket object from a phone number
        @param email: The phone number to request from RethinkDB
        @return: A Ticket object instantiated from the requested phone number, or None.
        """
        if phone == "None":
            return None
        else:
            try:
                db = rdb[cdb].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(
                    r.row['meta']['phone'] == phone
                ).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return Ticket(document['id'])
            except RqlRuntimeError:
                return None

    def __repr__(self):
        return u'<Ticket {} Source: {} Name: {} Phone: {} Email: {} Archived: {}>'.format(
            self.id, self.source, self.name, self.phone, self.email, self.archived)