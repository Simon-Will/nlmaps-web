from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class NLQueryForm(FlaskForm):
    nl = StringField('NL Query', validators=[DataRequired()])


class MRLQueryForm(FlaskForm):
    mrl = StringField('MRL Query', validators=[DataRequired()])
