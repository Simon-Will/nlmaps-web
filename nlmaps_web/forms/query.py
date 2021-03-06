import json

from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, Optional, ValidationError

from nlmaps_tools.parse_mrl import Symbol

from nlmaps_web.forms.base import BaseForm
from nlmaps_web.forms.fields import JSONStringField
from nlmaps_web.utils.helper import sort_nwr


class NlQueryForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])


class MrlQueryForm(BaseForm):
    mrl = StringField('MRL Query', validators=[DataRequired()])


class DiagnoseForm(BaseForm):
    nl = StringField('NL Query', validators=[DataRequired()])
    mrl = StringField('MRL Query', validators=[DataRequired()])


def to_tuple_with_symbols(l):
    parts = []
    for elm in l:
        if isinstance(elm, str):
            if elm in ('latlong', 'count') or elm.isdigit():
                elm = Symbol(elm)
            parts.append(elm)
        elif isinstance(elm, (list, tuple)):
            parts.append(to_tuple_with_symbols(elm))
        else:
            parts.append(str(elm))
    return tuple(parts)


def coerce_to_qtype(s):
    try:
        l = json.loads(s)
    except json.JSONDecodeError:
        return None

    if not isinstance(l, list):
        return None

    return to_tuple_with_symbols(l)


def is_json(form, field):
    try:
        json.loads(field.data)
    except:
        raise ValidationError('Not valid JSON')


class QueryFeaturesForm(BaseForm):
    query_type = SelectField(
        'Question Class', default='around_query',
        choices=[('in_query', 'Thing in Area'),
                 ('around_query', 'Thing around Reference Point'),
                 ('dist_closest', 'Distance to Closest Thing'),
                 ('dist_between', 'Distance between Two Things')],
        validators=[DataRequired()]
    )

    target_nwr = JSONStringField(
        'Target Tags', validators=[DataRequired()]
    )

    center_nwr = JSONStringField('Reference Point')
    area = StringField('Area')
    maxdist = SelectField(
        'Maximum Distance',
        choices=[('', '[No distance]'),
                 ('WALKING_DIST', 'Walking distance (WALKING_DIST)'),
                 ('DIST_INTOWN', 'Distance inside a town (DIST_INTOWN)'),
                 ('DIST_OUTTOWN', 'Larger distance, around a town (DIST_OUTTOWN)'),
                 ('DIST_DAYTRIP', 'Day trip (DIST_DAYTRIP)'),
                 ('CUSTOM', '[Custom distance] (Enter below)')],
    )
    custom_maxdist = IntegerField('Custom Distance (in m)',
                                  validators=[Optional()])

    #around_topx = IntegerField(
    #    'Limit to at Most',
    #    validators=[Optional()]
    #)
    around_topx = SelectField(
        'Limit to', default='',
        choices=[('', '[No Limit]'), ('1', 'Closest')],
    )

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
        coerce=coerce_to_qtype,
        validators=[DataRequired()]
    )

    cardinal_direction = SelectField(
        'Cardinal Direction', choices=['', 'east', 'north', 'south', 'west'],
        validators=[Optional()]
    )

    target_nwr_2 = JSONStringField(
        'Target Tags 2',
    )
    area_2 = StringField('Area 2')

    cardinal_direction_2 = SelectField(
        'Cardinal Direction 2', choices=['', 'east', 'north', 'south', 'west'],
        validators=[Optional()]
    )

    for_ = HiddenField()
    unit = HiddenField()

    # for_ and unit are not currently in use.

    #for_ = SelectField(
    #    'Distance Method', choices=[
    #        ('', 'Linear Distance'),
    #        ('walk', 'Distance by Foot'),
    #        ('bicycle', 'Distance by Bike'),
    #        ('car', 'Distance by Car'),
    #    ],
    #    validators=[DataRequired()]
    #)

    #unit = SelectField(
    #    'Distance Unit', choices=[
    #        ('', 'Don???t care'),
    #        ('km', 'Metric'),
    #        ('mi', 'Imperial'),
    #    ],
    #)

    def validate(self, *args, **kwargs):
        success = super().validate(*args, **kwargs)
        if success:
            if self.query_type.data == 'around_query':
                if not self.maxdist.data:
                    success = False
                    if not isinstance(self.maxdist.errors, list):
                        self.maxdist.errors = []
                    self.maxdist.errors.append('This field is required.')
                elif (self.maxdist.data == 'CUSTOM'
                      and not self.custom_maxdist.data):
                    success = False
                    if not isinstance(self.custom_maxdist.errors, list):
                        self.custom_maxdist.errors = []
                    self.custom_maxdist.errors.append(
                        'When choosing a custom distance, you must enter one.')

        return success

    def get_features(self):
        features = {
            'target_nwr': sort_nwr(self.target_nwr.data),
            'qtype': self.qtype.data,
        }
        dist_features = {}
        dist_between = self.query_type.data == 'dist_between'
        if self.query_type.data in ('dist_closest', 'dist_between'):
            dist_features['query_type'] = 'dist'
        else:
            features['query_type'] = self.query_type.data
            if self.maxdist.data:
                if self.maxdist.data == 'CUSTOM' and self.custom_maxdist.data:
                    features['maxdist'] = Symbol(str(self.custom_maxdist.data))
                else:
                    features['maxdist'] = Symbol(self.maxdist.data)
            if self.around_topx.data:
                features['around_topx'] = Symbol(str(self.around_topx.data))

        if (self.center_nwr.data
            and (features.get('query_type') == 'around_query'
                 or self.query_type.data == 'dist_closest')):
            features['query_type'] = 'around_query'
            features['center_nwr'] = sort_nwr(self.center_nwr.data)
        else:
            features['query_type'] = 'in_query'

        if self.area.data:
            features['area'] = self.area.data.strip()
        if self.cardinal_direction.data:
            features['cardinal_direction'] = self.cardinal_direction.data

        if dist_features:
            if self.for_.data:
                dist_features['for'] = self.for_.data
            if self.unit.data:
                dist_features['unit'] = Symbol(self.unit.data)

            dist_features['sub'] = [features]

            if dist_between:
                features_2 = {'qtype': (Symbol('latlong'),),
                              'query_type': 'in_query'}
                if self.target_nwr_2.data:
                    features_2['target_nwr'] = sort_nwr(self.target_nwr_2.data)
                if self.area_2.data:
                    features_2['area'] = self.area_2.data.strip()
                if self.cardinal_direction_2.data:
                    features_2['cardinal_direction'] = (self.cardinal_direction_2
                                                        .data)
                dist_features['sub'].append(features_2)
            else:
                features['maxdist'] = Symbol('DIST_INTOWN')
                features['around_topx'] = Symbol('1')

            features = dist_features

        print('Getting features: {}'.format(features))
        return features
