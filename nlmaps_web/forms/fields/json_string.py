import json

from wtforms import Field
from wtforms.widgets import TextInput


class JSONStringField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return json.dumps(self.data)
        return ''

    def process_data(self, value):
        if not value:
            value = None
        self.data = value

    def process_formdata(self, valuelist):
        if valuelist:
            val = valuelist[0]
            if val:
                try:
                    self.data = json.loads(val)
                except json.JSONDecodeError:
                    raise ValueError('Invalid JSON: {}'.format(val))

