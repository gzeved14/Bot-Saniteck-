import os
import telebot
import pyodbc
import re
import threading
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# --- CONFIGURAÇÃO DE ACESSO ---
USUARIOS_AUTORIZADOS = [1932518276] 

def get_db_connection():
    drivers = ["{ODBC Driver 17 for SQL Server}", "{SQL Server Native Client 11.0}", "{SQL Server}"]
    for driver in drivers:
        try:
            conn_str = (f"DRIVER={driver};SERVER={os.getenv('DB_SERVER')};"
                        f"DATABASE={os.getenv('DB_DATABASE')};UID={os.getenv('DB_USER')};"
                        f"PWD={os.getenv('DB_PASS')};TrustServerCertificate=yes;Connection Timeout=10;")
            conn = pyodbc.connect(conn_str, autocommit=False)
            if conn: return conn
        except: continue
    return None

def run_query(query, params=None):
    conn = get_db_connection()
    if not conn: raise ConnectionError("Erro de conexão com o banco de dados.")
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    return cursor.fetchall()

def formatar_data_protheus(texto_data):
    data_limpa = re.sub(r'[-/]', '', texto_data)
    try:
        if len(data_limpa) == 8:
            obj_data = datetime.strptime(data_limpa, "%d%m%Y")
            return obj_data.strftime("%Y%m%d")
        return None
    except: return None

# --- COMANDOS ---

@bot.message_handler(commands=['start', 'ajuda'])
def send_welcome(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    help_text = (
        "🤖 *Maracanã BI - Menu Completo:*\n\n"
        "💰 `/vendas` [data] - Faturamento (SF2)\n"
        "🏆 `/vendedores` [data] - Ranking do dia (SF2/SA3)\n"
        "📊 `/mensal` - Acumulado do mês (SF2)\n"
        "📦 `/produtos` [data] - Top 5 itens vendidos (SD2)\n"
        "🎯 `/oportunidades` [num] - Ver funil ou OP específica (AD1)\n"
        "⏳ `/carteira` - Pedidos em aberto (SC5)\n"
        "🏦 `/financeiro` [data] - Títulos a receber (SE1)"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['oportunidades', 'status'])
def buscar_oportunidade(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    try:
        args = message.text.split()
        if len(args) < 2:
            query = "SELECT COUNT(*) FROM AD1010 WHERE D_E_L_E_T_ = '' AND AD1_STATUS = '1'"
            qtd = run_query(query)[0][0]
            return bot.reply_to(message, f"🎯 *Total de Oportunidades Abertas:* {qtd}")
        
        num_op = args[1].zfill(6)
        query = "SELECT AD1_DESCRI, AD1_STATUS FROM AD1010 WHERE D_E_L_E_T_ = '' AND AD1_NROPOR = ?"
        rows = run_query(query, [num_op])
        
        if rows:
            desc, st = rows[0]
            status_txt = "✅ Aberto" if st == '1' else "📁 Fechado"
            bot.reply_to(message, f"📋 *OP:* {num_op}\n📝 {str(desc).strip()}\n🚩 Status: {status_txt}", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Oportunidade {num_op} não encontrada.")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['vendas'])
def vendas_dinamico(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    args = message.text.split()
    data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
    label_data = "Hoje"
    if len(args) > 1:
        data_f = formatar_data_protheus(args[1])
        if data_f: data_query = f"'{data_f}'"; label_data = args[1]
        else: return bot.reply_to(message, "⚠️ Use o formato DD/MM/AAAA")

    query = f"SELECT SUM(F2_VALBRUT) FROM SF2010 WHERE D_E_L_E_T_ = '' AND F2_EMISSAO = {data_query}"
    try:
        total = run_query(query)[0][0] or 0.0
        bot.reply_to(message, f"💰 *Faturamento ({label_data}):*\nR$ {total:,.2f}", parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['vendedores'])
def ranking_dinamico(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    args = message.text.split()
    data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
    label_data = "Hoje"
    if len(args) > 1:
        data_f = formatar_data_protheus(args[1])
        if data_f: data_query = f"'{data_f}'"; label_data = args[1]

    query = f"""
    SELECT TOP 5 A3_NOME, SUM(F2_VALBRUT) AS TOTAL FROM SF2010 F2
    INNER JOIN SA3010 A3 ON A3_COD = F2_VEND1 AND A3.D_E_L_E_T_ = ''
    WHERE F2.D_E_L_E_T_ = '' AND F2_EMISSAO = {data_query}
    GROUP BY A3_NOME ORDER BY TOTAL DESC
    """
    try:
        rows = run_query(query)
        res = f"🏆 *Top 5 Vendedores ({label_data})*\n" + "-"*25 + "\n"
        if not rows: res += "Sem vendas faturadas."
        for i, r in enumerate(rows, 1):
            res += f"{i}º {str(r[0]).strip()}: *R$ {r[1]:,.2f}*\n"
        bot.reply_to(message, res, parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['mensal'])
def ranking_mes(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    query = """
    SELECT TOP 5 A3_NOME, SUM(F2_VALBRUT) AS TOTAL FROM SF2010 F2
    INNER JOIN SA3010 A3 ON A3_COD = F2_VEND1 AND A3.D_E_L_E_T_ = ''
    WHERE F2.D_E_L_E_T_ = '' 
      AND F2_EMISSAO >= CONVERT(VARCHAR(6), GETDATE(), 112) + '01' 
      AND F2_EMISSAO <= CONVERT(VARCHAR(8), GETDATE(), 112)
    GROUP BY A3_NOME ORDER BY TOTAL DESC
    """
    try:
        rows = run_query(query)
        res = "📊 *Ranking Acumulado do Mês*\n" + "-"*25 + "\n"
        if not rows: res += "Sem vendas no mês."
        for i, r in enumerate(rows, 1):
            res += f"{i}º {str(r[0]).strip()}: *R$ {r[1]:,.2f}*\n"
        bot.reply_to(message, res, parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['produtos'])
def top_produtos(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    args = message.text.split()
    data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
    label_data = "Hoje"
    if len(args) > 1:
        data_f = formatar_data_protheus(args[1])
        if data_f: data_query = f"'{data_f}'"; label_data = args[1]
    
    query = f"""
    SELECT TOP 5 D2_COD, D2_DESC, SUM(D2_QUANT) AS QTD
    FROM SD2010 WHERE D_E_L_E_T_ = '' AND D2_EMISSAO = {data_query}
    GROUP BY D2_COD, D2_DESC ORDER BY QTD DESC
    """
    try:
        rows = run_query(query)
        res = f"📦 *Top 5 Produtos ({label_data})*\n" + "-"*25 + "\n"
        if not rows: res += "Nenhum item vendido."
        for r in rows:
            nome_prod = str(r[1]).strip() if r[1] else "Sem Descrição"
            res += f"🔹 {nome_prod} ({int(r[2])} un)\n"
        bot.reply_to(message, res, parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['carteira'])
def carteira_pedidos(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    query = """
    SELECT SUM(C6.C6_VALOR) 
    FROM SC6010 C6
    INNER JOIN SC5010 C5 ON C5.C5_NUM = C6.C6_NUM 
        AND C5.C5_FILIAL = C6.C6_FILIAL 
        AND C5.D_E_L_E_T_ = ''
    WHERE C6.D_E_L_E_T_ = '' 
      AND C5.C5_NOTA = '' -- Pedidos não faturados
      """
    try:
        total = run_query(query)[0][0] or 0.0
        bot.reply_to(message, f"⏳ *Pedidos Pendentes (Carteira):*\nR$ {total:,.2f}", parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

@bot.message_handler(commands=['financeiro'])
def financeiro_dia(message):
    if message.from_user.id not in USUARIOS_AUTORIZADOS: return
    args = message.text.split()
    data_query = "CONVERT(VARCHAR(8), GETDATE(), 112)"
    label_data = "Hoje"
    if len(args) > 1:
        data_f = formatar_data_protheus(args[1])
        if data_f: data_query = f"'{data_f}'"; label_data = args[1]

    query = f"SELECT SUM(E1_VALOR) FROM SE1010 WHERE D_E_L_E_T_ = '' AND E1_EMISSAO = {data_query}"
    try:
        total = run_query(query)[0][0] or 0.0
        bot.reply_to(message, f"🏦 *Títulos Gerados em {label_data}:*\nR$ {total:,.2f}", parse_mode="Markdown")
    except Exception as e: bot.reply_to(message, f"⚠️ Erro: {e}")

# --- LOG E BLOQUEIO ---
@bot.message_handler(func=lambda message: True)
def log_e_bloqueio(message):
    print(f"👤 {message.from_user.first_name} ({message.from_user.id}): {message.text}")
    if message.from_user.id not in USUARIOS_AUTORIZADOS:
        bot.reply_to(message, "🚫 Acesso Negado.")
    else:
        bot.reply_to(message, "💡 Comando não reconhecido. Use /ajuda.")

print("🤖 Bot Maracanã Online v2.1 (Full Load)...")
bot.infinity_polling()