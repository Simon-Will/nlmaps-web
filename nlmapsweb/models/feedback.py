from sqlalchemy import Column, Unicode

from nlmapsweb.models.base import BaseModel


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
