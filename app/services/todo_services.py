
import random
from datetime import timedelta
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session
from app.models.todo import Todo, TodoPriority, TodoStatus
from app.schemas.todo import TodoCreate, TodoUpdate
from app.utils.helpers import generate_uuid7, utcnow


_VERBS = [
    "Selesaikan", "Siapkan", "Review", "Kirim", "Perbaiki", "Pelajari", "Update",
    "Jadwalkan", "Buat", "Cek", "Revisi", "Diskusikan", "Rapikan", "Tes",
]
_OBJECTS = [
    "laporan keuangan bulanan", "dokumentasi API", "desain halaman login",
    "jadwal meeting tim", "email ke klien", "bug di halaman checkout",
    "presentasi proyek", "backup database", "data pelanggan", "proposal anggaran",
    "unit test modul pembayaran", "tampilan dashboard", "kontrak vendor",
    "materi training", "daftar belanja kantor", "server staging",
]
_NOTES = [
    "Prioritaskan sebelum akhir minggu.",
    "Koordinasikan dulu dengan tim terkait.",
    "Perlu persetujuan dari atasan.",
    "Sudah ada draft awal, tinggal dirapikan.",
    "Tunggu masukan dari klien.",
    "Catat hasilnya di dokumen bersama.",
    "Cek ulang sebelum dikirim.",
]
SORTABLE_COLUMNS = {
    "created_at": Todo.created_at,
    "updated_at": Todo.updated_at,
    "title": Todo.title,
    "status": Todo.status,      
    "priority": Todo.priority,  
}


# CREATE
def create_todo(db: Session, data: TodoCreate) -> Todo:
    """Insert satu todo. id (UUID v7), created_at, updated_at diisi otomatis oleh model."""
    todo = Todo(**data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo) 
    return todo


# READ
def get_todo(db: Session, todo_id: str) -> Todo | None:
    """Ambil satu todo berdasarkan id. Mengembalikan None kalau tidak ada."""
    return db.get(Todo, todo_id)


#UPDATE
def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    """Update sebagian field. Hanya field yang dikirim client yang diubah."""
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        if value is None and field != "description":
            continue
        setattr(todo, field, value)
    db.commit() 
    db.refresh(todo)
    return todo

def list_todos(
    db: Session,
    *,
    status: list[TodoStatus] | None = None,
    priority: list[TodoPriority] | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Todo], int]:

    # 1) FILTERING
    conditions = []
    if status:
        conditions.append(Todo.status.in_(status))      
    if priority:
        conditions.append(Todo.priority.in_(priority))
    if search:
        conditions.append(Todo.title.icontains(search, autoescape=True))

    # 2) Hitung total data yang cocok filter (untuk info pagination).
    total = db.scalar(select(func.count()).select_from(Todo).where(*conditions)) or 0
    # 3) SORTING: Tentukan kolom dan arah pengurutan.
    column = SORTABLE_COLUMNS[sort_by]
    descending = order == "desc"
    order_by = (
        (column.desc(), Todo.id.desc()) if descending else (column.asc(), Todo.id.asc())
    )

    # 4) PAGINATION: Offset + Limit untuk ambil halaman tertentu.
    stmt = (
        select(Todo)
        .where(*conditions)
        .order_by(*order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(db.scalars(stmt).all())
    return items, total

#  DELETE
def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()


# SEED
def seed_random_todos(db: Session, count: int = 1000) -> int:
    now = utcnow()
    statuses = list(TodoStatus)
    priorities = list(TodoPriority)

    rows = []
    for _ in range(count):
        created_at = now - timedelta(
            seconds=random.randint(0, 30 * 24 * 3600),
            microseconds=random.randint(0, 999_999),
        )
        updated_at = created_at + timedelta(
            seconds=random.randint(0, int((now - created_at).total_seconds()))
        )
        rows.append(
            {
                "id": generate_uuid7(),
                "title": f"{random.choice(_VERBS)} {random.choice(_OBJECTS)}",
                "status": random.choice(statuses),
                "priority": random.choice(priorities),
                "description": " ".join(random.sample(_NOTES, k=2)) if random.random() > 0.2 else None,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

    db.execute(insert(Todo), rows)  # bulk insert
    db.commit()                     # commit sekali saja
    return count