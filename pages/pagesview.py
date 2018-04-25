
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Imports
########################################################################################################################

# System imports
from time import sleep

# Flask imports
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify

# Flask-login imports
from flask_login import current_user, login_required

# Flask-classful imports
from flask_classful import FlaskView, route

# Flask-WTF imports
from pages.pagesform import PageForm

# rethink imports
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# rethink configuration
from app.config import rdb
# This Class uses database configuration:
cdb = 'pagedb'

# Pull in our local model
from pages.pagesmodel import Page

########################################################################################################################
## View Class
########################################################################################################################
class PagesView(FlaskView):
    #decorators = [login_required]

    #def index():
    #        form = AuthForm()
    #        if form.validate_on_submit():
    #                r.table('users').insert({"name":form.label.data}).run(g.rdb_conn)
    #                return redirect(url_for('index'))
    #        selection = list(r.table('users').run(g.rdb_conn))
    #        return render_template('index.html', form = form, tasks = selection)



    def index(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields({'meta': {'title': True}})
        ).filter(
            lambda this_user: this_user.has_fields({'meta': {'updated_at': True}})
        #).filter(  # Old ISO8601-in-string format
        #    lambda row:row['updated_at'].match("^2014")
        #).filter(  # Rethink is unhappy with some lambda expressions
        #    lambda updated_at:
        #    updated_at.during(r.now() - 604800, r.now())
        #).filter(  # This works, but it's ugly
        #    r.row['meta']['updated_at'].during(r.time(2014, 1, 1, 'Z'), r.now())
        #).filter(  # Very Yes?
        #    r.row['meta']['updated_at'].during(r.now() - 300, r.now() + 300)
        ).order_by(
            r.desc(r.row['meta']['updated_at'])
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            print("Length is: ", len(selection), " so expanding items.")
            single = False
            if len(selection) <= 15:
                single = True
            #ticking = r.expr({'now': r.now(), 'ten_ago': r.now() - 300, 'future': r.now() + 300}).run(g.rdb_conn)
            return render_template('pages/pagelist.html', results=selection, single=single) #, thetimeis=ticking)
        else:
            return "Not Found", 404

    @login_required
    def create_page(self):
        """
        Display of a Flask-WTF form for Page Content creation.
        @return: A redirect to a Jinja2 Template containing a form
        """
        form = PageForm()
        # Populate the form.
        new_page = Page.create("new-untitled-page", "New Page", "This page is blank.")
        if new_page is not None:
            print("Pages.create_page: Created Page in DB: {}".format(new_page))
            uuid = new_page.id
        return redirect(url_for('PagesView:edit_page', uuid=uuid))


    @login_required
    def destroy_page(self, uuid):
        """
        Destroy a Page object.
        @return: A redirect to the pages list.
        """
        this_page = Page.delete(uuid)
        if this_page is not None:
            print("Pages.destroy_page: Destroyed Page from DB: {}".format(uuid))
            flash('Page Destroyed', 'success')
        return redirect(url_for('PagesView:index'))

    @login_required
    def edit_page(self, uuid):
        """
        Display of a Flask-WTF form for Page Content Updates.
        @return: A Jinja2 Template containing a form
        """
        form = PageForm()
        # Populate the form.
        this_page = Page(uuid)
        if this_page is not None:
            print("Pages.edit_page: Retrieved Page from DB: {}".format(this_page))
            form.object_id.data = this_page.object_id
            form.title.data = this_page.title
            form.content.data = this_page.content
        return render_template('pages/pageform.html', form=form, page_uuid=uuid)

        
    @login_required
    @route('do_edit_page/<uuid>', methods=['POST'])
    def do_edit_page(self, uuid):
        """
        Processing of a User Submitted Ticket Flask-WTF form
        @return: A Jinja2 Template containing a Ticket form, or a redirect to the index or next page.
        """
        form = PageForm()
        if form.validate_on_submit():
            page = Page.update(uuid, form.object_id.data, form.title.data, form.content.data)
            flash('Page Edited', 'success')
            return redirect(request.args.get('next') or url_for('PagesView:index'))
        return render_template('pages/pageform.html', form=form)

    def get(self, uuid):
        this_page = Page(uuid)
        if this_page is not None:
            print("Pages.get: Retrieved Page from DB: {}".format(this_page))
            return render_template('pages/page.html', results=this_page)  # , results={this_page})
        else:
            return "Not Found", 404

    def get_page(self, uuid):
        this_page = Page(uuid)
        if this_page is not None:
            print("Pages.get_page: Retrieved Page from DB: {}".format(this_page))
            return render_template('pages/page.html', results=this_page)  # , results={this_page})
        else:
            return "Not Found", 404

    def get_json(self, uuid):
        db = rdb[cdb].split(':')
        this_page = r.db(db[0]).table(db[1]).get(uuid).run(g.rdb_conn)
        if this_page is not None:
            print("Pages.get_json: Retrieved Page from DB: {}".format(this_page))
            return jsonify(this_page)
        else:
            return "Not Found", 404

    def get_all(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 15:
                print("Length is: ", len(selection), " so expanding items.")
                single = True

            return render_template('pages/pagelist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def find_history(self, past=600):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields({'meta': {'title': True}})
        ).filter(
            lambda this_user: this_user.has_fields({'meta': {'updated_at': True}})
        ).filter(
            r.row['meta']['updated_at'].during(r.now() - int(past), r.now() + 3600)
        ).order_by(
            r.desc(r.row['meta']['updated_at'])
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 15:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('pages/pagelist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def today(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields({'meta': {'title': True}})
        ).filter(
            lambda this_user: this_user.has_fields({'meta': {'updated_at': True}})
        ).filter(
            r.row['meta']['updated_at'].during(r.now() - 86400, r.now() + 3600)
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 15:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('pages/pagelist.html', results=selection, single=single)
        else:
            return "Not Found", 404

    def this_week(self):
        db = rdb[cdb].split(':')
        selection = list(r.db(db[0]).table(db[1]).filter(
            lambda this_user: this_user.has_fields({'meta': {'title': True}})
        ).filter(
            lambda this_user: this_user.has_fields({'meta': {'updated_at': True}})
        ).filter(
            r.row['meta']['updated_at'].during(r.now() - 604800, r.now() + 3600)
        ).run(g.rdb_conn))
        if selection is not None:
            #print(selection)
            single = False
            if len(selection) <= 15:
                print("Length is: ", len(selection), " so expanding items.")
                single = True
            return render_template('pages/pagelist.html', results=selection, single=single)
        else:
            return "Not Found", 404
