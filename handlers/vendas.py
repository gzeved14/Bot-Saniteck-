from services.protheus_service import ProtheusService
from middleware.auth import auth_required
from utils.formatters import format_money, ranking
from utils.date_utils import formatar_data_protheus
from utils.cache import get_cache, set_cache

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
            args = message.text.split()[1:]
            segmento_filtro = "geral"
            data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)" # Hoje no SQL
            label_data = "Hoje"

            for arg in args:
                arg_lower = arg.lower()
                if arg_lower in ['privado', 'público', 'publico']:
                    segmento_filtro = "publico" if arg_lower in ['público', 'publico'] else "privado"
                else:
                    # Se não for segmento, tenta formatar como data do dia
                    data_f = formatar_data_protheus(arg)
                    if data_f:
                        data_query = f"'{data_f}'"
                        label_data = arg

            rows = service.ranking_vendedores_completo(segmento=segmento_filtro, data_especifica=data_query)
            
            emojis = {"geral": "🏆", "publico": "🏛️", "privado": "🏢"}
            titulo = f"{emojis[segmento_filtro]} Ranking {segmento_filtro.title()} ({label_data})"
            bot.reply_to(message, ranking(titulo, rows), parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao gerar ranking de vendedores.")

    @bot.message_handler(commands=['mensalvendedores'])
    @auth_required
    def mensal(message):
        try:
            args = message.text.split()[1:]
            segmento_filtro = "geral"
            ano_mes_query = None
            label_data = "Mês Atual"

            for arg in args:
                arg_lower = arg.lower()
                if arg_lower in ['privado', 'público', 'publico']:
                    segmento_filtro = "publico" if arg_lower in ['público', 'publico'] else "privado"
                elif '/' in arg and len(arg) == 7:
                    mes, ano = arg.split('/')
                    ano_mes_query = f"{ano}{mes}"
                    label_data = arg

            rows = service.ranking_vendedores_completo(segmento=segmento_filtro, ano_mes=ano_mes_query)
            
            emojis = {"geral": "📊", "publico": "🏛️", "privado": "🏢"}
            titulo = f"{emojis[segmento_filtro]} Ranking Acumulado {segmento_filtro.title()} ({label_data})"
            bot.reply_to(message, ranking(titulo, rows), parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao gerar ranking mensal.")
    
    @bot.message_handler(commands=['mensalvendas'])
    @auth_required
    def mensalvendas(message):
        try:
            args = message.text.split()[1:]
            segmento_filtro = "geral"
            ano_mes_query = None
            label_data = "Mês Atual"

            for arg in args:
                arg_lower = arg.lower()
                if arg_lower in ['privado', 'público', 'publico']:
                    segmento_filtro = "publico" if arg_lower in ['público', 'publico'] else "privado"
                elif '/' in arg and len(arg) == 7:
                    mes, ano = arg.split('/')
                    ano_mes_query = f"{ano}{mes}"
                    label_data = arg

            # Chamando a função do Service que retorna o dicionário {"privado": X, "publico": Y}
            dados = service.mensalvendas(ano_mes_query) 
            
            publico = dados["publico"]
            privado = dados["privado"]
            total_geral = publico + privado

            # Restante do código de montagem da resposta...
            if segmento_filtro == "privado":
                resposta = f"🏢 *Faturamento Privado ({label_data}):*\n{format_money(privado)}"
            elif segmento_filtro == "publico":
                resposta = f"🏛️ *Faturamento Público ({label_data}):*\n{format_money(publico)}"
            else:
                resposta = (
                    f"📊 *Faturamento Mensal ({label_data})*\n"
                    f"━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🏛️ *Público:* `{format_money(publico)}`\n"
                    f"🏢 *Privado:* `{format_money(privado)}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"💰 *Total Geral:* `{format_money(total_geral)}`"
                )

            bot.reply_to(message, resposta, parse_mode="Markdown")

        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao consultar faturamento mensal.")