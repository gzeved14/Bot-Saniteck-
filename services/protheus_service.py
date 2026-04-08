from database.connection import get_connection
from utils.cache import get_cache, set_cache

class ProtheusService:

    def run_query(self, query, params=None):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or [])
                return cursor.fetchall()
        except Exception:
            # Mantendo seu padrão de lançar Timeout para o handler tratar
            raise TimeoutError("Erro ao acessar o Protheus. Verifique a VPN.")

    # --- COMERCIAL ---
    def vendas(self, data):
        cache_key = f"vendas:{data}"
        cached = get_cache(cache_key)
        if cached: return cached

        # Importante: Sempre filtrar D_E_L_E_T_ no Protheus
        query = f"SELECT SUM(F2_VALBRUT) FROM SF2010 WHERE D_E_L_E_T_ = '' AND F2_EMISSAO = {data}"

        result = self.run_query(query)[0][0] or 0.0
        set_cache(cache_key, result, 60)
        return result

    def ranking_vendedores(self, data):
        # Join com SA3 filtrando deletados em ambas as tabelas
        query = f"""
        SELECT TOP 5 RTRIM(A3_NOME), SUM(F2_VALBRUT) AS TOTAL
        FROM SF2010 F2
        INNER JOIN SA3010 A3 ON A3_COD = F2_VEND1 AND A3.D_E_L_E_T_ = ''
        WHERE F2.D_E_L_E_T_ = '' AND F2_EMISSAO = {data}
        GROUP BY A3_NOME ORDER BY TOTAL DESC
        """
        return self.run_query(query)

    def mensal(self):
        cache_key = "mensal"
        cached = get_cache(cache_key)
        if cached: return cached

        query = """
        SELECT TOP 5 RTRIM(A3_NOME), SUM(F2_VALBRUT) AS TOTAL
        FROM SF2010 F2
        INNER JOIN SA3010 A3 ON A3_COD = F2_VEND1 AND A3.D_E_L_E_T_ = ''
        WHERE F2.D_E_L_E_T_ = '' 
          AND F2_EMISSAO >= CONVERT(VARCHAR(6), GETDATE(), 112) + '01'
        GROUP BY A3_NOME ORDER BY TOTAL DESC
        """
        result = self.run_query(query)
        set_cache(cache_key, result, 120)
        return result

    # --- LOGISTICA ---
    def produtos(self, data):
        # CORREÇÃO CRÍTICA: Subquery para buscar descrição da SB1 e evitar duplicidade
        query = f"""
        SELECT TOP 5 
            RTRIM(D2_COD), 
            (SELECT TOP 1 RTRIM(B1_DESC) FROM SB1010 B1 WHERE B1.B1_COD = D2.D2_COD AND B1.D_E_L_E_T_ = '') AS DESCRI,
            SUM(D2_QUANT) AS QTD
        FROM SD2010 D2
        WHERE D_E_L_E_T_ = '' AND D2_EMISSAO = {data}
        GROUP BY D2_COD 
        ORDER BY QTD DESC
        """
        return self.run_query(query)

    # --- CRM ---
    def oportunidades(self, num=None):
        if not num:
            return self.run_query(
                "SELECT COUNT(*) FROM AD1010 WHERE D_E_L_E_T_ = '' AND AD1_STATUS = '1'"
            )[0][0]

        return self.run_query(
            "SELECT RTRIM(AD1_DESCRI), AD1_STATUS FROM AD1010 WHERE D_E_L_E_T_ = '' AND AD1_NROPOR = ?",
            [num.zfill(6)]
        )

    # --- BACKOFFICE ---
    def carteira(self):
        cache_key = "carteira"
        cached = get_cache(cache_key)
        if cached: return cached

        # Carteira real: Pedidos na SC6 que estão na SC5 e não foram faturados
        query = """
        SELECT SUM(C6_VALOR) 
        FROM SC6010 C6
        INNER JOIN SC5010 C5 ON C5.C5_NUM = C6.C6_NUM AND C5.D_E_L_E_T_ = ''
        WHERE C6.D_E_L_E_T_ = '' AND C5.C5_NOTA = ''
        """
        result = self.run_query(query)[0][0] or 0.0
        set_cache(cache_key, result, 120)
        return result

    def financeiro(self, data):
        query = f"""
        SELECT SUM(E1_VALOR)
        FROM SE1010
        WHERE D_E_L_E_T_ = '' AND E1_EMISSAO = {data}
        """
        return self.run_query(query)[0][0] or 0.0
    
    # No protheus_service.py
def run_query(self, query, params=None):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ ERRO SQL REAL: {e}") # Isso vai aparecer no 'docker logs'
        raise e