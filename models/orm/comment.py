from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship

from models.orm.post import Post
from tools.orm import Base


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    author: Mapped[str] = Column(String(length=128), nullable=False)
    body: Mapped[str] = Column(String(496), nullable=False)
    parent_comment_id: Mapped[int] = Column(Integer, nullable=False, default=0, index=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    nesting_level: Mapped[int] = Column(Integer, nullable=False, default=0)
    created_date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date: Mapped[datetime] = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    post_id: Mapped[Post] = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"))
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment: {self.id}>"
