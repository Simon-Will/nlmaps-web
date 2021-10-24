from wtforms import StringField

from nlmaps_web.forms.parsing_model import ParsingModelForm


class ValidationsForm(ParsingModelForm):
    label = StringField('Label')
