from typing import Any, Collection, Dict, List

from flask_wtf import FlaskForm
from wtforms.widgets import HiddenInput, SubmitInput


class BaseForm(FlaskForm):

    def get_non_hidden_fields(self):
        return [field for field in self
                if not isinstance(field.widget, (HiddenInput, SubmitInput))]

    def get_data(self, exclude: Collection = tuple()) -> Dict[str, Any]:
        return {name: field.data for name, field in self._fields.items()
                if name not in exclude}

    @property
    def formatted_errors(self) -> List[str]:
        """All validation errors as formatted strings

        These strings are supposed to be ready to be displayed to the
        user.

        :return: List of formatted errors
        """
        formatted_errors = []
        for potential_field_name, errors in self.errors.items():
            try:
                field = self[potential_field_name]
                pre_colon = field.label.text
            except KeyError:
                pre_colon = potential_field_name

            for error in errors:
                formatted_errors.append(
                    f'Error with {pre_colon}: {error}'
                )

        return formatted_errors
