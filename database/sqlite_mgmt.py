import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "usuarios.db")

def get_sqlite_conn():
    return sqlite3.connect(DB_PATH)
def init_sqlite():
    """Cria as tabelas necessárias e o usuário admin inicial."""
    with get_sqlite_conn() as conn:
        cursor = conn.cursor()
        # CRÍTICO: O nome da tabela deve ser 'users' porque é o que seu middleware busca
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL
            )
        """)
        
        # Insere você como primeiro usuário para você não ser bloqueado pelo bot
        # Substituí pelo seu ID que vimos nos logs
        cursor.execute("INSERT OR IGNORE INTO users (user_id, nome) VALUES (?, ?)", 
                       (1932518276, 'Eduardo Admin'))
        conn.commit()
    print("✅ SQLite inicializado e tabelas verificadas.")