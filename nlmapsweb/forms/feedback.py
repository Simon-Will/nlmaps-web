from flask import current_app
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm


class FeedbackExportForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.choices = [
            (model, model)
            for model in current_app.config['MODELS'].keys()
        ]

    model = SelectField('Reference Model', choices=[])
    correct = BooleanField('Correct Instances', default=True)
    incorrect = BooleanField('Incorrect Instances', default=True)


class FeedbackForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    systemMrl = StringField('System MRL Query')
    correctMrl = StringField('Correct MRL Query')

