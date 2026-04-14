import os

from database.sqlite_mgmt import add_user
from middleware.auth import verificar_acesso


def get_admin_id():
    try:
        return int(os.getenv("ADMIN_USER_ID", ""))
    except ValueError:
        return None

def register(bot):
    @bot.message_handler(commands=['meuid'])
    def meuid(message):
        user_id = message.from_user.id
        bot.reply_to(message, f"Seu ID: `{user_id}`", parse_mode="Markdown")

    @bot.message_handler(commands=['autorizar'])
    def autorizar(message):
        admin_id = get_admin_id()

        if admin_id is None:
            bot.reply_to(message, "⚠️ ADMIN_USER_ID não configurado no ambiente.")
            return

        if message.from_user.id != admin_id:
            bot.reply_to(message, "❌ Apenas o administrador pode autorizar usuários.")
            return

        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "⚠️ Use: /autorizar ID NOME")
            return

        try:
            novo_id = int(args[1])
            novo_nome = " ".join(args[2:])
            if add_user(novo_id, novo_nome):
                bot.reply_to(message, f"✅ {novo_nome} autorizado!")
            else:
                bot.reply_to(message, "ℹ️ Usuário já autorizado.")
        except ValueError:
            bot.reply_to(message, "❌ ID inválido.")

    @bot.message_handler(commands=['start', 'ajuda'])
    def send_welcome(message):
        admin_id = get_admin_id()
        is_admin = admin_id is not None and message.from_user.id == admin_id

        if not verificar_acesso(message.from_user.id):
            help_text = (
                "🤖 *Maracanã BI - Acesso Pendente*\n\n"
                "🆔 `/meuid` - Mostra seu ID do Telegram\n"
                "🔐 Peça ao administrador para liberar seu acesso com `/autorizar ID NOME`\n"
                "⚠️ Depois da liberação, você terá acesso aos relatórios e menus do bot"
            )
            bot.reply_to(message, help_text, parse_mode="Markdown")
            return

        help_text = (
            "🤖 *Maracanã BI - Menu Principal*\n\n"
            "🆔 `/meuid` - Mostra seu ID do Telegram\n"
            "💰 `/vendas` - Faturamento do dia\n"
            "🏆 `/vendedores` - Ranking de hoje\n"
            "📊 `/mensal` - Acumulado do mês\n"
            "📦 `/produtos` - Top 5 itens vendidos\n"
            "🎯 `/oportunidades` - Funil de vendas\n"
            "⏳ `/carteira` - Pedidos pendentes\n"
            "🏦 `/financeiro` - Títulos gerados"
        )

        if is_admin:
            help_text = help_text.replace(
                "🆔 `/meuid` - Mostra seu ID do Telegram\n",
                "🆔 `/meuid` - Mostra seu ID do Telegram\n"
                "✅ `/autorizar ID NOME` - Autoriza um novo usuário (admin)\n"
            )

        bot.reply_to(message, help_text, parse_mode="Markdown")