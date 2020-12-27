from flask import current_app
from wtforms import SelectField

from nlmapsweb.forms.base import BaseForm
from nlmapsweb.models.users import User


class ParsingModelForm(BaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model.choices = [
            (model, model)
            for model in current_app.config['MODELS']
        ]

    model = SelectField('Model', choices=[])


class AdminParsingModelForm(ParsingModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users = User.query.all()
        self.user.choices = [(-1, '<All Users>')]
        self.user.choices.extend([(user.id, user.name) for user in users])

    user = SelectField('User', choices=[])
