from wtforms import HiddenField, SelectMultipleField

from nlmapsweb.app import db
from nlmapsweb.forms.base import BaseForm
from nlmapsweb.forms.fields.string_list import StringListField
from nlmapsweb.models.tags import Tag
from nlmapsweb.models.parse_taggings import ParseTagging


class ParseTaggingForm(BaseForm):

    def __init__(self, *args, feedback_id=None, parse_log_id=None, **kwargs):
        super().__init__(*args, **kwargs)

        available_tags = [tag.name for tag in Tag.query.all()]
        self.tags.choices = [(tag, tag) for tag in available_tags]
        if self.tags.choices:
            self.tags_size = len(self.tags.choices)

        if feedback_id and parse_log_id:
            given_tag_ids = db.session.query(ParseTagging.tag_id).filter(
                ParseTagging.feedback_id == feedback_id,
                ParseTagging.parse_log_id == parse_log_id,
            )
            tag_names = [
                tag.name
                for tag in Tag.query.filter(Tag.id.in_(given_tag_ids))
            ]
            self.tags.process_data(tag_names)
            self.feedback_id.process_data(feedback_id)
            self.parse_log_id.process_data(parse_log_id)

    feedback_id = HiddenField()
    parse_log_id = HiddenField()
    tags = SelectMultipleField('Tags', choices=[])
    new_tags = StringListField('New Tags (comma-separated)')
