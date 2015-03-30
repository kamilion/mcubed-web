#!/usr/bin/env python2.7
## This program contains tools for searching through a rethinkdb server.
# Copyright (c) 2014 SLLabs.com <support@sllabs.com>
# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
# Written in 2014 for Kamilion@SLLabs.com by ircs://irc.ospnet.org/#sllabs residents
# See http://files.sllabs.com/files/storage/xen/MAINTAINERS.txt for details.

# "If you have an apple and I have an apple and we exchange these apples
# then you and I will still each have one apple.
# But if you have an idea and I have an idea and we exchange these ideas,
# then each of us will have two ideas." -- George Bernard Shaw

from commandr import command, Run

# RethinkDB imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError
try:
    conn = r.connect()
except RqlDriverError:
    print("Failed to connect to rethinkdb. Check the daemon status and try again.")

### Local functions
def verify_rethinkdb_tables(dbname, tablename):
    try:
        result = r.db_create(dbname).run(conn)
        print("DB: {} database created: {}".format(dbname, result))
    except RqlRuntimeError:
        print("DB: {} database found.".format(dbname))
    try:
        result = r.db(dbname).table_create(tablename).run(conn)
        print("DB: {} table created: {}".format(tablename, result))
    except RqlRuntimeError:
        print("DB: {} table found.".format(tablename))

@command('spew', category='Server')
def spew(dbname, tablename):
    """Spews data from a running rethinkdb server.
    Arguments:
      dbname - The Database Name.
      tablename - The Table Name.
    """
    verify_rethinkdb_tables(dbname, tablename)
    all_records = r.db(dbname).table(tablename).run(conn)
    if all_records:
	print("Yessssss!")
        for document in all_records:
            print(document)
    else:
        print("Nnnnoooo.")


@command('copytable', category='Server')
def spew(olddbname, oldtablename, newdbname, newtablename):
    """Copies table data from a running rethinkdb server.
    Arguments:
      olddbname - The Source Database Name.
      oldtablename - The Source Table Name.
      newdbname - The New Database Name.
      newtablename - The New Table Name.
    """
    verify_rethinkdb_tables(olddbname, oldtablename)
    verify_rethinkdb_tables(newdbname, newtablename)
    all_records = r.db(olddbname).table(oldtablename).run(conn)
    if all_records:
        for document in all_records:
            #print(document)
            r.db(newdbname).table(newtablename).insert(document).run(conn)
	print("Yessssss!")
    else:
        print("Nnnnoooo.")

 

@command('redate', category='Server')
def redate(dbname, tablename, fieldname):
    """Redates a running rethinkdb server.
    Arguments:
      dbname - The Database Name.
      tablename - The Table Name.
      fieldname - The Field Name.
    """
    verify_rethinkdb_tables(dbname, tablename)
    all_records = r.db(dbname).table(tablename).pluck(fieldname, 'id').run(conn)
    if all_records:
	print("Yessssss!")
        print(dir(all_records))
        for document in all_records:
            for item in document:
                print(item)
            #print(dir(document))
            #help(document)
            #if document.updated_at:
                #print(document.updated_at)
            #print(document)
    else:
        print("Nnnnoooo.")

if __name__ == '__main__':
    Run()

