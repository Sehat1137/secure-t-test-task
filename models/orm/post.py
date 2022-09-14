from datetime import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, relationship

from tools.orm import Base


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(length=248), nullable=False)
    article: Mapped[str] = Column(Text, nullable=False)
    created_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date: Mapped[datetime] = Column(DateTime, nullable=True)
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", lazy="joined")

    def __repr__(self):
        return f"<Post: {self.id}>"
