import difflib
import json

from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel
from nlmapsweb.models.feedback_tag_association import feedback_tag_association


class Feedback(BaseModel):

    __tablename__ = 'feedback'

    nl = Column(
        Unicode(500),
        nullable=False,
    )

    systemMrl = Column(
        Unicode(500),
        nullable=True,
    )

    correctMrl = Column(
        Unicode(500),
        nullable=True,
    )

    tags = relationship(
        'Tag',
        secondary=feedback_tag_association,
        back_populates='feedback_pieces'
    )

    def system_is_correct(self) -> bool:
        return self.systemMrl and self.systemMrl == self.correctMrl

    @property
    def type(self):
        if not self.systemMrl:
            return 'system-error'

        if self.correctMrl:
            if self.systemMrl == self.correctMrl:
                return 'correct'
            else:
                return 'incorrect'
        else:
            return 'unknown'

    def get_sys_to_corr_opcodes(self, as_json=False):
        if self.type == 'incorrect':
            opcodes = difflib.SequenceMatcher(
                a=self.systemMrl, b=self.correctMrl).get_opcodes()
        else:
            opcodes = None

        if as_json:
            opcodes = json.dumps(opcodes)

        return opcodes
