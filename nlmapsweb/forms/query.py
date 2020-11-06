from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired

from nlmapsweb.forms.base import BaseForm


class QueryFeaturesForm(BaseForm):
    query_type = SelectField(
        'Query Class', default='around_query',
        choices=[('in_query', 'Thing in Area'), ('around_query', 'Thing around Reference Point')],
        validators=[DataRequired()]
    )
    target_nwr = StringField('Target Tags', validators=[DataRequired()])
    center_nwr = StringField('Reference Point')
    area = StringField('Area')
    maxdist = StringField('Maximum Distance')
    around_topx = IntegerField('Limit to at Most')
    qtype = SelectField(
        'QType', choices=[
            # Although there are other qtypes, there are most important.
            ('["latlong"]', 'latlong'),
            ('["count"]', 'count'),
            ('[["least",["topx","1"]]]', 'least(topx(1))'),
            ('[["findkey","name"]]', 'findkey(name)'),
            ('[["findkey","opening_hours"]]', 'findkey(opening_hours)'),
            ('[["findkey","website"]]', 'findkey(website)'),
            ('[["findkey","wheelchair"]]', 'findkey(wheelchair)'),
        ],
        validators=[DataRequired()]
    )
    cardinal_direction = SelectField(
        'Cardinal Direction', choices=['', 'east', 'north', 'south', 'west']
    )


class NlQueryForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])


class MrlQueryForm(BaseForm):
    mrl = StringField('MRL Query', validators=[DataRequired()])


class DiagnoseForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    mrl = StringField('MRL Query', validators=[DataRequired()])
