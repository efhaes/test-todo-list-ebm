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

## Video Demo
https://drive.google.com/file/d/1xyOQ-YCQIrN6sfHjhctSwJq9f-ueIiir/view?usp=sharing
