import math
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.todo import Todo, TodoPriority, TodoStatus
from app.schemas.todo import (SeedResponse,TodoCreate,TodoListResponse,TodoRead,TodoUpdate,)
from app.services import todo_services


router = APIRouter(prefix="/todos", tags=["Todos"])


def _get_todo_or_404(db: Session, todo_id: UUID) -> Todo:
    todo = todo_services.get_todo(db, str(todo_id))
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo tidak ditemukan")
    return todo


@router.get("", response_model=TodoListResponse, summary="Daftar todo (filter, sort, pagination)")
def list_todos(
    # filtering
    status: list[TodoStatus] | None = Query(
        None, description="Filter status. Boleh lebih dari satu: ?status=pending&status=done"
    ),
    priority: list[TodoPriority] | None = Query(
        None, description="Filter priority. Boleh lebih dari satu: ?priority=high&priority=medium"
    ),
    search: str | None = Query(None, min_length=1, max_length=100, description="Cari kata di title"),
    # sorting
    sort_by: Literal["created_at", "updated_at", "title", "status", "priority"] = Query(
        "created_at", description="Kolom untuk pengurutan"
    ),
    order: Literal["asc", "desc"] = Query("desc", description="Arah pengurutan"),
    # Pagination
    page: int = Query(1, ge=1, description="Nomor halaman (mulai dari 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Jumlah data per halaman (maks 100)"),
    db: Session = Depends(get_db),
):
    items, total = todo_services.list_todos(
        db,
        status=status,
        priority=priority,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    return TodoListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size),  # 0 kalau tidak ada data
    )


@router.post("", response_model=TodoRead, status_code=201, summary="Tambah satu todo")
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    return todo_services.create_todo(db, payload)

@router.post("/seed", response_model=SeedResponse, status_code=201, summary="Insert data random (default 1000)")
def seed_todos(
    count: int = Query(1000, ge=1, le=10000, description="Jumlah data random yang dibuat"),
    db: Session = Depends(get_db),
):
    inserted = todo_services.seed_random_todos(db, count)
    return SeedResponse(inserted=inserted)


@router.get("/{todo_id}", response_model=TodoRead, summary="Detail satu todo")
def get_todo(todo_id: UUID, db: Session = Depends(get_db)):
    return _get_todo_or_404(db, todo_id)


@router.patch("/{todo_id}", response_model=TodoRead, summary="Update sebagian field todo")
def update_todo(todo_id: UUID, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = _get_todo_or_404(db, todo_id)
    return todo_services.update_todo(db, todo, payload)


@router.delete("/{todo_id}", status_code=204, summary="Hapus todo")
def delete_todo(todo_id: UUID, db: Session = Depends(get_db)):
    todo = _get_todo_or_404(db, todo_id)
    todo_services.delete_todo(db, todo)
    return Response(status_code=204) 