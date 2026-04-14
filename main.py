import os
import telebot
from dotenv import load_dotenv
from handlers import vendas, logistica, crm, financeiro, geral
from database.sqlite_mgmt import init_sqlite

def main():
	init_sqlite()
	load_dotenv()

	token = os.getenv("TELEGRAM_TOKEN")
	if not token:
		raise ValueError("TELEGRAM_TOKEN não encontrado no ambiente.")

	admin_user_id = os.getenv("ADMIN_USER_ID")
	if not admin_user_id:
		raise ValueError("ADMIN_USER_ID não encontrado no ambiente.")
	if not admin_user_id.isdigit():
		raise ValueError("ADMIN_USER_ID deve ser numérico.")

	bot = telebot.TeleBot(token)

	# registrar handlers
	geral.register(bot)
	vendas.register(bot)
	logistica.register(bot)
	crm.register(bot)
	financeiro.register(bot)

	print("🤖 Bot Online (Arquitetura Modular)...")
	bot.infinity_polling()


if __name__ == "__main__":
	main()