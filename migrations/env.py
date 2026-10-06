"""
migrations/env.py
-----------------
Dijalankan Alembic setiap kali kamu menjalankan perintah `alembic ...`.
Tugasnya: memberi tahu Alembic (1) database mana yang dituju dan
(2) tabel apa saja yang ada di model kita.
"""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import settings
from app.core.database import Base

# Import model WAJIB supaya tabel `todos` terdaftar di Base.metadata.
# Tanpa ini, `alembic revision --autogenerate` akan menghasilkan migration kosong.
from app.models.todo import Todo  # noqa: F401

config = context.config

if config.config_file_name is not None:
    # disable_existing_loggers=False: jangan matikan logger milik aplikasi
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Daftar tabel yang dikenal Alembic, dipakai untuk membandingkan model vs database.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Mode offline: tidak konek ke database, hanya mencetak SQL-nya.
    Dipakai dengan: alembic upgrade head --sql
    """
    context.configure(
        url=settings.DATABASE_URL.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Mode online (default): konek ke MySQL lalu menjalankan migration.
    URL koneksi diambil dari .env lewat `settings`, jadi tidak ada
    password yang tersimpan di alembic.ini.
    """
    # NullPool: koneksi langsung ditutup setelah selesai (cocok untuk script sekali jalan)
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # deteksi perubahan tipe kolom saat autogenerate
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()