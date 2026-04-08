from services.protheus_service import ProtheusService
from middleware.auth import auth_required
from utils.formatters import format_money, ranking
from utils.date_utils import formatar_data_protheus

service = ProtheusService()

def register(bot):
    @bot.message_handler(commands=['vendas'])
    @auth_required
    def vendas(message):
        try:
            args = message.text.split()
            data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
            label = "Hoje"

            if len(args) > 1:
                data_f = formatar_data_protheus(args[1])
                if data_f:
                    data_query = f"'{data_f}'"
                    label = args[1]

            total = service.vendas(data_query)
            bot.reply_to(message, f"💰 *Faturamento ({label}):*\n{format_money(total)}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao consultar vendas.")

    @bot.message_handler(commands=['vendedores'])
    @auth_required
    def vendedores(message):
        try:
            args = message.text.split()
            data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
            label = "Hoje"

            if len(args) > 1:
                data_f = formatar_data_protheus(args[1])
                if data_f:
                    data_query = f"'{data_f}'"
                    label = args[1]

            rows = service.ranking_vendedores(data_query)
            bot.reply_to(message, ranking(f"🏆 Ranking ({label})", rows), parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao gerar ranking.")

    @bot.message_handler(commands=['mensal'])
    @auth_required
    def mensal(message):
        try:
            rows = service.mensal()
            bot.reply_to(message, ranking("📊 Ranking Acumulado (Mês)", rows), parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao gerar ranking mensal.")