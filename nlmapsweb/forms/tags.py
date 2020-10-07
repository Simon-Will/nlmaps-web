from wtforms import HiddenField, SelectMultipleField

from nlmapsweb.forms.base import BaseForm
from nlmapsweb.forms.fields.string_list import StringListField
from nlmapsweb.models.tags import Tag


class FeedbackTagsForm(BaseForm):

    def __init__(self, *args, feedback_piece=None, **kwargs):
        super().__init__(*args, **kwargs)
        available_tags = [tag.name for tag in Tag.query.all()]
        self.tags.choices = [(tag, tag) for tag in available_tags]
        if feedback_piece:
            self.tags.process_data([tag.name for tag in feedback_piece.tags])
            self.feedback_id.process_data(feedback_piece.id)

    feedback_id = HiddenField()
    tags = SelectMultipleField('Tags', choices=[])
    new_tags = StringListField('New Tags (comma-separated)')
