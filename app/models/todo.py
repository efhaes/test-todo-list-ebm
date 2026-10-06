
import enum
from datetime import datetime

from sqlalchemy import CHAR, DateTime, Enum, String, Text
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.utils.helpers import generate_uuid7, utcnow

class TodoStatus(str, enum.Enum):
    PENDING = "pending"
    PROGRESS = "progress"
    DONE = "done"


class TodoPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def _enum_values(enum_class) -> list[str]:
    return [member.value for member in enum_class]

DateTimeMicro = DateTime().with_variant(DATETIME(fsp=6), "mysql")


# --- Model: tabel `todos` ---
class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=generate_uuid7)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[TodoStatus] = mapped_column(
        Enum(TodoStatus, values_callable=_enum_values, name="todo_status"),
        nullable=False,default=TodoStatus.PENDING,index=True,  # kolom ini sering dipakai untuk filter
    )
    priority: Mapped[TodoPriority] = mapped_column(
        Enum(TodoPriority, values_callable=_enum_values, name="todo_priority"),
        nullable=False,default=TodoPriority.MEDIUM,index=True, 
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTimeMicro, nullable=False, default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTimeMicro, nullable=False, default=utcnow, onupdate=utcnow
    )
    def __repr__(self) -> str:
        return f"<Todo id={self.id} title={self.title!r} status={self.status.value}>"