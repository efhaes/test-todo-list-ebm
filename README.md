# Todo List API


Stack: Python 3.10 · FastAPI · SQLAlchemy 2.0 · Alembic · MySQL 8 | Frontend: Vue 3 + Vite


# Backend (root project)
pip install -r requirements.txt
# salin .env.example menjadi .env, isi kredensial MySQL
# buat database `todo_db` (utf8mb4) terlebih dulu
alembic upgrade head
uvicorn app.main:app --reload      # Swagger: http://127.0.0.1:8000/docs

# Frontend
cd frontend && npm install && npm run dev      # http://localhost:5173
```

## Endpoint

| Method | Endpoint | Keterangan |
| --- | --- | --- |
| GET | `/todos` | Daftar todo (filter, sort, pagination) |
| POST | `/todos` | Tambah satu todo |
| POST | `/todos/seed?count=1000` | Insert data random (default 1000) |
| GET / PATCH / DELETE | `/todos/{id}` | Detail / ubah sebagian / hapus |

**Parameter `GET /todos`:** `status` dan `priority` (boleh diulang, mis. `?status=pending&status=done`), `search` (judul), `sort_by` (`created_at`, `updated_at`, `title`, `status`, `priority`), `order` (`asc`/`desc`), `page`, `page_size` (maks 100).

## Catatan Teknis

- Sorting memakai whitelist kolom, dan `id` jadi pembeda kedua supaya pagination stabil.
- Seed 1000 data memakai satu bulk insert dan satu commit.
- ID memakai UUID v7 (`CHAR(36)`), waktu disimpan UTC dengan presisi mikrodetik.
- Struktur tabel dikelola Alembic, bukan `create_all()`.

## Video Demo

_isi link YouTube di sini_