from wtforms import StringField
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm


class FeedbackForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    systemMrl = StringField('System MRL Query')
    correctMrl = StringField('Correct MRL Query')
