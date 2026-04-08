# handlers/geral.py
import os

# Pega os usuários autorizados do .env (ajuste conforme seu middleware se necessário)
USUARIOS_AUTORIZADOS = [1932518276] 

def register(bot):
    @bot.message_handler(commands=['start', 'ajuda'])
    def send_welcome(message):
        # Verificação simples de acesso (enquanto não migramos pro SQLite)
        if message.from_user.id not in USUARIOS_AUTORIZADOS:
            bot.reply_to(message, "🚫 Acesso Negado. Fale com o Eduardo.")
            return

        help_text = (
            "🤖 *Maracanã BI - Menu Principal*\n\n"
            "💰 `/vendas` - Faturamento do dia\n"
            "🏆 `/vendedores` - Ranking de hoje\n"
            "📊 `/mensal` - Acumulado do mês\n"
            "📦 `/produtos` - Top 5 itens vendidos\n"
            "🎯 `/oportunidades` - Funil de vendas\n"
            "⏳ `/carteira` - Pedidos pendentes\n"
            "🏦 `/financeiro` - Títulos gerados"
        )
        bot.reply_to(message, help_text, parse_mode="Markdown")