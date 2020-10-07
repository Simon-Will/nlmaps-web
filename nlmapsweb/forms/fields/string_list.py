from typing import List, Optional

from wtforms import Field
from wtforms.widgets import TextInput

class StringListField(Field):
    """Field for representing a list of strings

    Built on a TextInput widget, this field assumes that the text in the
    widget is a string separated by a separator (a comma by default).
    Surrounding whitespace is stripped from the list elements (i.e. it's
    OK to put a space after a comma in the widget) and empty elements
    are deleted (i.e. an empty widget will yield an empty list).

    If you provide data to this field via `obj` or `data`, make sure
    that it is a List[str] already.
    """
    widget = TextInput()

    def __init__(self, *args, **kwargs):
        """Initialize the field with `sep` as a separator"""
        self.sep = kwargs.pop('sep', ',')
        super().__init__(*args, **kwargs)

    def _value(self):
        """Provide the current value for the widget"""
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return self.sep.join(self.data)
        else:
            return ''

    def process_data(self, value: Optional[List[str]]):
        if not value:
            value = []
        # noinspection PyAttributeOutsideInit
        self.data = value

    def process_formdata(self, valuelist: List[str]):
        if valuelist:
            list_as_string = valuelist[0]
            if list_as_string is None:
                data = []
            elif not isinstance(list_as_string, str):
                raise ValueError(f'Not a string: {list_as_string}')
            else:
                # Non-empty string. This is the normal case.
                try:
                    data = [
                        part.strip()
                        for part in list_as_string.split(self.sep)
                    ]
                except (AttributeError, TypeError):
                    message = (
                        f'Not a valid {self.sep}-separated list:'
                        f' {list_as_string}'
                    )
                    raise ValueError(message)

            # Remove empty elements, i.e. 'foo,,bar' will result in
            # ['foo', 'bar'].
            # noinspection PyAttributeOutsideInit
            self.data = [elm for elm in data if elm]
