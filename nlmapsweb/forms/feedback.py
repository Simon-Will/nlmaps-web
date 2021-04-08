from flask import current_app
from wtforms import (BooleanField, HiddenField, IntegerField,
                     SelectField, StringField)
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm
from nlmapsweb.forms.parsing_model import ParsingModelForm
from nlmapsweb.models.users import User


class FeedbackExportForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.choices = [
            (model, model)
            for model in current_app.config['MODELS']
        ]

    model = SelectField('Reference Model', choices=[])
    correct = BooleanField('Correct Instances', default=True)
    incorrect = BooleanField('Incorrect Instances', default=True)


class FeedbackCreateForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    systemMrl = StringField('System MRL Query')
    correctMrl = StringField('Correct MRL Query')
    model = StringField('Model')
    parent_id = HiddenField()


class FeedbackEditForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    correct_mrl = StringField('Correct MRL Query')


class FeedbackListForm(ParsingModelForm):
    page = IntegerField('Page', default=1)
    nl_part = StringField('NL Substring')


class AdminFeedbackListForm(FeedbackListForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.query.all()
        self.user.choices = [(-1, '<All Users>')]
        self.user.choices.extend([(user.id, user.name) for user in users])

    user = SelectField('User', choices=[])
