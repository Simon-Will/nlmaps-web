from typing import Any, Collection, Dict

from flask_wtf import FlaskForm
from wtforms.widgets import HiddenInput, SubmitInput


class BaseForm(FlaskForm):

    def get_non_hidden_fields(self):
        return [field for field in self
                if not isinstance(field.widget, (HiddenInput, SubmitInput))]

    def get_data(self, exclude: Collection = tuple()) -> Dict[str, Any]:
        return {name: field.data for name, field in self._fields.items()
                if name not in exclude}
