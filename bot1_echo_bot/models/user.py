from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger, Text, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_echo_text: Mapped[str] = mapped_column(Text, nullable=True)
    
    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"