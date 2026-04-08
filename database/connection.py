import pyodbc
import sqlite3
import os
from contextlib import contextmanager
from database.config import DB_CONFIG

def init_sqlite():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    # Criando a tabela que o middleware está pedindo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            nome TEXT,
            authorized_by INTEGER
        )
    """)
    # Aproveita para se auto-autorizar se a tabela estiver vazia
    cursor.execute("INSERT OR IGNORE INTO users (user_id, nome) VALUES (?, ?)", (1932518276, 'Eduardo'))
    conn.commit()
    conn.close()

def build_connection_string():
    return (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['user']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate={DB_CONFIG['trust_cert']};"
        f"Connection Timeout={DB_CONFIG['timeout']};"
    )

@contextmanager
def get_connection():
    # No Docker (Linux), o driver costuma ser este:
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE')};"
        f"UID={os.getenv('DB_USER')};"
        f"PWD={os.getenv('DB_PASS')};"
        "TrustServerCertificate=yes;Connection Timeout=10;"
    )
    conn = pyodbc.connect(conn_str)
    try:
        yield conn
    finally:
        conn.close()