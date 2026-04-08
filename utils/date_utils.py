import re
from datetime import datetime

def formatar_data_protheus(texto_data):
    """
    Converte DD/MM/AAAA ou DD-MM-AAAA para YYYYMMDD (Padrão Protheus)
    """
    data_limpa = re.sub(r'[-/]', '', texto_data)
    try:
        if len(data_limpa) == 8:
            obj_data = datetime.strptime(data_limpa, "%d%m%Y")
            return obj_data.strftime("%Y%m%d")
        return None
    except Exception:
        return None