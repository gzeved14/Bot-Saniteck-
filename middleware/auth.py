from functools import wraps
from database.sqlite_mgmt import get_sqlite_conn

_bot = None


def set_bot(bot):
    global _bot
    _bot = bot

def verificar_acesso(user_id):
    """Consulta se o ID do Telegram está no banco de autorizados."""
    try:
        with get_sqlite_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        return False


def is_authorized(user_id):
    # Mantido por compatibilidade com chamadas existentes.
    return verificar_acesso(user_id)
    

def auth_required(func):
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if not verificar_acesso(message.from_user.id):
            if _bot is not None:
                return _bot.reply_to(message, "🚫 Acesso Negado.")
            return message.reply("🚫 Acesso Negado.")
        return func(message, *args, **kwargs)
    return wrapper