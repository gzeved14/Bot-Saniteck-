from services.protheus_service import ProtheusService
from middleware.auth import auth_required
from utils.date_utils import formatar_data_protheus # Ajuste o caminho conforme seu projeto

service = ProtheusService()

def register(bot):

    @bot.message_handler(commands=['produtos'])
    @auth_required
    def top_produtos(message):
        try:
            args = message.text.split()
            data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
            label_data = "Hoje"
            
            # Tratamento de data opcional (Ex: /produtos 08/04/2026)
            if len(args) > 1:
                data_f = formatar_data_protheus(args[1])
                if data_f: 
                    data_query = f"'{data_f}'"
                    label_data = args[1]
                else:
                    return bot.reply_to(message, "⚠️ Formato de data inválido. Use DD/MM/AAAA")

            # CHAMA O SERVIÇO (A query pesada fica lá no protheus_service.py)
            rows = service.produtos(data_query)
            
            res = f"📦 *Top 5 Produtos/Serviços ({label_data})*\n"
            res += "-"*25 + "\n"
            
            if not rows:
                res += "Nenhum movimento encontrado para esta data."
            else:
                for i, r in enumerate(rows, 1):
                    cod_prod = r[0]
                    desc_prod = r[1]
                    qtd = float(r[2])
                    
                    # Fallback: se a descrição na SB1 vier nula, mostra o código
                    nome_exibicao = desc_prod if desc_prod else f"Cód: {cod_prod}"
                    res += f"{i}º {nome_exibicao} ({qtd:,.0f} un)\n"
                    
            bot.reply_to(message, res, parse_mode="Markdown")

        except TimeoutError:
            bot.reply_to(message, "⏳ O banco de dados demorou a responder. Tente novamente.")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao gerar ranking de produtos.")
            print(f"Erro no Handler Logística: {e}")