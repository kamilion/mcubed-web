
########################################################################################################################
## Imports
########################################################################################################################

# Flask imports
from flask import flash
from flask.ext.wtf import Form
from flask.ext.login import current_user
from wtforms.fields import TextField, TextAreaField, PasswordField
from wtforms.validators import DataRequired

# Our own Pages model
from pages.pagesmodel import Page


########################################################################################################################
## Class Definitions
########################################################################################################################

class PageForm(Form):
    """
    A simple Page form.
    Will create Pages and may provide a Page object, if found, to the View.
    """
    title = TextField('title', validators=[DataRequired()])
    object_id = TextField('object_id', validators=[DataRequired()])
    content = TextAreaField('content', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Register a new a Page object via a Page class helper
        @param args: Arguments, in order of definition in class
        @param kwargs: Keyword based Arguments, in any order
        """
        Form.__init__(self, *args, **kwargs)
        self.page = None

    def validate(self):
        """
        Do validation of the form contents.
        @return: True if the Form object was successfully validated, or False if it was not.
        """
        rv = Form.validate(self)
        if not rv:
            flash('A required field is empty', 'error')
            return False

        # Don't create the page here in the validator anymore, instead, do it from the view definition.
        #page = Page.create(self.object_id.data, self.title.data, self.content.data)

        #if page is None:
        #    return False
        else:
            return True

