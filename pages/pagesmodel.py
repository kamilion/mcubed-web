
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
cdb = 'pagedb'

# Import regex support
import re

########################################################################################################################
## Helper Functions
########################################################################################################################

# Run these tasks when we're first imported by uwsgi or executed.
import pages.pagesdefaults as pagesdefaults
# db setup; only runs once
pagesdefaults.db_setup(cdb)


########################################################################################################################
## Utility Classes
########################################################################################################################

class NoSuchUUIDExists(Exception):
    pass


########################################################################################################################
## Pages Class
########################################################################################################################

# This class represents a Page in RethinkDB.
class Page():
    # Identifiers:
    # This is RethinkDB's internal UUID identifier for a document.
    id = None
    # Within the 'meta' hierarchy:
    # This is our internal object_id and IS NOT UNIQUE. 
    # This is used as an index to find multiple documents with the same object_id.
    # Multiple documents can make up a Page.
    object_id = None
    # This is the human-readable title of our page.
    title = None
    # This is a RethinkDB time object of when it was updated.
    updated_at = None
    # This dict contains content display instructions.
    content = {}
    # All other top level attributes are available from the RethinkDB document as part of the 'results' object itself.
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
            print("PAGESMODEL: InitPage: Critical Failure: Saving Throw Failed! while looking up Rethink UUID: {}".format(uuid))

        if results is None:
            raise NoSuchUUIDExists

        self.id = results['id']
        self.object_id = results['meta']['object_id']
        self.updated_at = results['meta']['updated_at']

        # These fields may potentially be missing.
        try:
            self.title = results['meta']['title']
        except KeyError:
            self.title = "0.0.0.0"
        try:
            self.content = results['meta']['content']
        except KeyError:
            self.content = {}

        print("PAGESMODEL: InitPage: {} Title: {} Object_ID: {}".format(
            self.id, self.title, self.object_id))


    # Convenience method
    @classmethod
    def create(cls, object_id, title, content):
        """
        Create a new machine entry from a object_id
        @param object_id: The object_id to register with RethinkDB
        @return: A Page object instantiated from the requested object_id, or None.
        """
        try:  # To make the database entry with the object_id
            db = rdb[cdb].split(':')
            inserted = r.db(db[0]).table(db[1]).insert(
                { 'meta': {
                    'updated_at': r.now(),
                    'object_id': object_id,
                    'title': title,
                    'content': content
                  }
                }
            ).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return Page(inserted['generated_keys'][0])

    # Convenience method
    @classmethod
    def update(cls, uuid, object_id, title, content):
        """
        Update a new machine entry from a object_id
        @param object_id: The object_id to register with RethinkDB
        @return: A Page object instantiated from the requested object_id, or None.
        """
        try:  # To update the database entry with the object_id
            db = rdb[cdb].split(':')
            inserted = r.db(db[0]).table(db[1]).get(uuid).update(
                { 'meta': {
                    'updated_at': r.now(),
                    'object_id': object_id,
                    'title': title,
                    'content': content
                  }
                }
            ).run(g.rdb_conn)
        except RqlRuntimeError:
            return None

        return Page(uuid)

    # Convenience method
    @classmethod
    def delete(cls, uuid):
        """
        Delete a Page object from a uuid
        @param uuid: The uuid to request RethinkDB to delete
        @return: A Page object instantiated from the requested article_id, or None.
        """
        if uuid == "None":
            return None
        else:
            try:
                db = rdb[cdb].split(':')
                deleted = r.db(db[0]).table(db[1]).get(uuid).delete().run(g.rdb_conn)
            except RqlRuntimeError:
                return None
        return True

    # Convenience method
    @classmethod
    def get_id_from_object_id(cls, object_id):
        """
        Create a Page object from a object_id
        @param object_id: The object_id to request from RethinkDB
        @return: A Page object instantiated from the requested article_id, or None.
        """
        if object_id == "None":
            return None
        else:
            try:
                db = rdb[cdb].split(':')
                cursor = r.db(db[0]).table(db[1]).filter(
                    r.row['meta']['object_id'] == object_id
                ).pluck('id').run(g.rdb_conn)
                for document in cursor:
                    return Page(document['id'])
            except RqlRuntimeError:
                return None

    def __repr__(self):
        return '<Page {} Title: {} Object_ID: {}>'.format(self.id, self.title, self.object_id)
