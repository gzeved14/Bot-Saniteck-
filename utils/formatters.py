def format_money(valor):
    return f"R$ {valor:,.2f}"

def ranking(titulo, rows):
    text = f"{titulo}\n" + "─"*25 + "\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}º 🥇 {r[0]} → *R$ {r[1]:,.2f}*\n"
    return text