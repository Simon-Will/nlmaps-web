from flask import current_app
from wtforms import SelectField

from nlmaps_web.forms.base import BaseForm


class ParsingModelForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.choices = [
            (model, model)
            for model in current_app.config['MODELS']
        ]

    model = SelectField('Model', choices=[])
