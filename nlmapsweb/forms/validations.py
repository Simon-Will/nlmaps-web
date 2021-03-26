from wtforms import StringField

from nlmapsweb.forms.parsing_model import ParsingModelForm


class ValidationsForm(ParsingModelForm):
    label = StringField('Label')
