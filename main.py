import os
import telebot
from dotenv import load_dotenv
from handlers import vendas, logistica, crm, financeiro, geral
from database.sqlite_mgmt import init_sqlite

init_sqlite()
load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# registrar handlers
geral.register(bot)
vendas.register(bot)
logistica.register(bot)
crm.register(bot)
financeiro.register(bot)

print("🤖 Bot Online (Arquitetura Modular)...")
bot.infinity_polling()