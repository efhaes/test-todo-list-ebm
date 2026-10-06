from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.todo import TodoPriority, TodoStatus


class TodoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(..., min_length=1, max_length=255, examples=["Tulis judul yang jelas"])
    status: TodoStatus = TodoStatus.PENDING        # default kalau tidak dikirim
    priority: TodoPriority = TodoPriority.MEDIUM   # default kalau tidak dikirim
    description: str | None = Field(
        None, examples=["Deskripsi lebih panjang, boleh dikosongkan"], max_length=1000
    )


class TodoUpdate(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(None, min_length=1, max_length=255)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None
    description: str | None = None


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: TodoStatus
    priority: TodoPriority
    description: str | None
    created_at: datetime   # UTC
    updated_at: datetime   # UTC


class TodoListResponse(BaseModel):
    items: list[TodoRead]
    total: int         
    page: int          
    page_size: int     
    total_pages: int   


class SeedResponse(BaseModel):
    inserted: int