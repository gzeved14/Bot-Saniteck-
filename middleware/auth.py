import sqlite3
from functools import wraps
from database.sqlite_mgmt import get_sqlite_conn # Use a função que criamos!

def is_authorized(user_id):
    try:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"Erro no Middleware: {e}")
        return False
    
def auth_required(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if not is_authorized(message.from_user.id):
            return message.reply("🚫 Acesso Negado.")
        return func(message, *args, **kwargs)
    return wrapper