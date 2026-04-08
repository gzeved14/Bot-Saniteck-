from services.protheus_service import ProtheusService
from middleware.auth import auth_required

service = ProtheusService()

def register(bot):
    @bot.message_handler(commands=['oportunidades'])
    @auth_required
    def oportunidades(message):
        try:
            args = message.text.split()
            if len(args) == 1:
                total = service.oportunidades()
                bot.reply_to(message, f"🎯 *Oportunidades Abertas:* {total}", parse_mode="Markdown")
            else:
                num_op = args[1]
                rows = service.oportunidades(num_op)
                if rows:
                    row = rows[0]
                    status_txt = "✅ Aberto" if str(row[1]) == '1' else "📁 Fechado"
                    bot.reply_to(message, f"📋 *OP:* {num_op}\n📝 {str(row[0]).strip()}\n🚩 Status: {status_txt}", parse_mode="Markdown")
                else:
                    bot.reply_to(message, f"❌ Oportunidade {num_op} não encontrada.")
        except Exception as e:
            bot.reply_to(message, "⚠️ Erro ao consultar CRM.")