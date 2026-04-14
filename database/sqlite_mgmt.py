import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("SQLITE_DB_PATH", os.path.join(BASE_DIR, "usuarios.db"))


def get_sqlite_conn():
    return sqlite3.connect(DB_PATH)


def init_sqlite():
    """Cria a tabela de usuários e insere você como Admin."""
    with get_sqlite_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            )
        """)

        admin_id = os.getenv("ADMIN_USER_ID")
        admin_name = os.getenv("ADMIN_USER_NAME", "Administrador")
        if admin_id:
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, nome) VALUES (?, ?)",
                (int(admin_id), admin_name),
            )
        conn.commit()
    print("✅ Banco SQLite (usuários) pronto.")


def add_user(user_id, nome):
    """Insere um novo usuário na lista de autorizados."""
    try:
        with get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (user_id, nome) VALUES (?, ?)", (user_id, nome))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False