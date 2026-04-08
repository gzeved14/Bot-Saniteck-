from services.protheus_service import ProtheusService
from middleware.auth import auth_required
from utils.formatters import format_money
from utils.date_utils import formatar_data_protheus # Certifique-se de ter essa util

service = ProtheusService()

def register(bot):
    @bot.message_handler(commands=['carteira'])
    @auth_required
    def carteira(message):
        try:
            total = service.carteira()
            bot.reply_to(message, f"⏳ *Pedidos em Carteira:*\n{format_money(total)}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao consultar carteira.")

    @bot.message_handler(commands=['financeiro'])
    @auth_required
    def financeiro(message):
        try:
            args = message.text.split()
            data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
            label = "Hoje"

            if len(args) > 1:
                data_f = formatar_data_protheus(args[1])
                if data_f:
                    data_query = f"'{data_f}'"
                    label = args[1]

            total = service.financeiro(data_query)
            bot.reply_to(message, f"🏦 *Financeiro ({label}):*\n{format_money(total)}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao consultar financeiro.")