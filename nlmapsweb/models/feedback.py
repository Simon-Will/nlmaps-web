from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship

from nlmapsweb.models.base import BaseModel
from nlmapsweb.processing.comparing import get_feedback_type, get_opcodes


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

    parse_taggings = relationship('ParseTagging', back_populates='feedback_piece')

    def system_is_correct(self) -> bool:
        return self.systemMrl and self.systemMrl == self.correctMrl

    @property
    def type(self):
        return get_feedback_type(self.systemMrl, self.correctMrl)

    @property
    def opcodes(self):
        return get_opcodes(self.systemMrl, self.correctMrl)

    @property
    def opcodes_json(self):
        return get_opcodes(self.systemMrl, self.correctMrl, as_json=True)
