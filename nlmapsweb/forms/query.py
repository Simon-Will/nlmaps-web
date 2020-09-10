from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm


class NlQueryForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])


class MrlQueryForm(BaseForm):
    mrl = StringField('MRL Query', validators=[DataRequired()])


class DiagnoseForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    mrl = StringField('MRL Query', validators=[DataRequired()])
