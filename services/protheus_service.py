from database.connection import get_connection
from utils.cache import get_cache, set_cache

class ProtheusService:

    def run_query(self, query, params=None):
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or [])
                return cursor.fetchall()
        except Exception as e:
            # Print para debug via docker logs
            print(f"❌ ERRO SQL: {e}")
            raise TimeoutError("Erro ao acessar o Protheus. Verifique a VPN.")

    # --- COMERCIAL ---

    def vendas(self, data):
        """Retorna o faturamento diário total (Geral)"""
        cache_key = f"vendas:{data}"
        cached = get_cache(cache_key)
        if cached: return cached

        query = f"SELECT SUM(F2_VALBRUT) FROM SF2010 WHERE D_E_L_E_T_ = '' AND F2_EMISSAO = {data}"
        result = self.run_query(query)
        
        valor = 0.0
        if result and result[0][0]:
            valor = float(result[0][0])

        set_cache(cache_key, valor, 60)
        return valor

    def mensalvendas(self, ano_mes=None):
        """
        Retorna um dicionário com os valores separados por segmento.
        O Handler espera: {'privado': X, 'publico': Y}
        """
        cache_key = f"mensalvendas_segmentos_{ano_mes if ano_mes else 'atual'}"
        cached = get_cache(cache_key)
        if cached: return cached

        if ano_mes:
            condicao_data = f"F2_EMISSAO LIKE '{ano_mes}%'"
        else:
            condicao_data = "F2_EMISSAO >= CONVERT(VARCHAR(6), GETDATE(), 112) + '01'"

        # Query única que já faz a separação pelo campo A1_XTIPO que descobrimos
        query = f"""
        SELECT 
            ISNULL(SUM(CASE WHEN A1.A1_XTIPO = '1' THEN F2.F2_VALBRUT ELSE 0 END), 0) AS PRIVADO,
            ISNULL(SUM(CASE WHEN A1.A1_XTIPO <> '1' OR A1.A1_XTIPO IS NULL OR A1.A1_XTIPO = '' THEN F2.F2_VALBRUT ELSE 0 END), 0) AS PUBLICO
        FROM SF2010 F2
        INNER JOIN SA1010 A1 ON A1.A1_COD = F2.F2_CLIENTE AND A1.A1_LOJA = F2.F2_LOJA AND A1.D_E_L_E_T_ = ''
        WHERE F2.D_E_L_E_T_ = '' AND {condicao_data}
        """
        
        result = self.run_query(query)
        
        # Prepara o dicionário para o Handler consumir
        res_dict = {"privado": 0.0, "publico": 0.0}
        if result:
            res_dict["privado"] = float(result[0][0])
            res_dict["publico"] = float(result[0][1])

        set_cache(cache_key, res_dict, 120)
        return res_dict

    def ranking_vendedores_completo(self, segmento="geral", data_especifica=None, ano_mes=None):
        tipo_busca = f"dia_{data_especifica}" if data_especifica else f"mes_{ano_mes if ano_mes else 'atual'}"
        cache_key = f"ranking_vendedores_{segmento}_{tipo_busca}"
        
        cached = get_cache(cache_key)
        if cached: return cached

        if data_especifica:
            condicao_data = f"F2_EMISSAO = {data_especifica}"
        elif ano_mes:
            condicao_data = f"F2_EMISSAO LIKE '{ano_mes}%'"
        else:
            condicao_data = "F2_EMISSAO >= CONVERT(VARCHAR(6), GETDATE(), 112) + '01'"

        if segmento == "privado":
            filtro_segmento = "AND A1.A1_XTIPO = '1'"
        elif segmento == "publico":
            filtro_segmento = "AND (A1.A1_XTIPO <> '1' OR A1.A1_XTIPO IS NULL OR A1.A1_XTIPO = '')"
        else:
            filtro_segmento = ""

        query = f"""
        SELECT TOP 5 RTRIM(A3_NOME) AS VENDEDOR, SUM(F2_VALBRUT) AS TOTAL
        FROM SF2010 F2
        INNER JOIN SA3010 A3 ON A3_COD = F2_VEND1 AND A3.D_E_L_E_T_ = ''
        INNER JOIN SA1010 A1 ON A1.A1_COD = F2.F2_CLIENTE AND A1.A1_LOJA = F2.F2_LOJA AND A1.D_E_L_E_T_ = ''
        WHERE F2.D_E_L_E_T_ = '' AND {condicao_data} {filtro_segmento}
        GROUP BY A3_NOME ORDER BY TOTAL DESC
        """
        
        result = self.run_query(query)
        set_cache(cache_key, result, 120)
        return result

    # --- LOGISTICA / BACKOFFICE ---

    def produtos(self, data):
        query = f"""
        SELECT TOP 5 RTRIM(D2_COD), 
        (SELECT TOP 1 RTRIM(B1_DESC) FROM SB1010 B1 WHERE B1.B1_COD = D2.D2_COD AND B1.D_E_L_E_T_ = '') AS DESCRI,
        SUM(D2_QUANT) AS QTD
        FROM SD2010 D2 WHERE D_E_L_E_T_ = '' AND D2_EMISSAO = {data}
        GROUP BY D2_COD ORDER BY QTD DESC
        """
        return self.run_query(query)

    def carteira(self):
        cache_key = "carteira"
        cached = get_cache(cache_key)
        if cached: return cached
        query = "SELECT SUM(C6_VALOR) FROM SC6010 C6 INNER JOIN SC5010 C5 ON C5.C5_NUM = C6.C6_NUM AND C5.D_E_L_E_T_ = '' WHERE C6.D_E_L_E_T_ = '' AND C5.C5_NOTA = ''"
        result = self.run_query(query)[0][0] or 0.0
        set_cache(cache_key, result, 120)
        return result

    def financeiro(self, data):
        query = f"SELECT SUM(E1_VALOR) FROM SE1010 WHERE D_E_L_E_T_ = '' AND E1_EMISSAO = {data}"
        result = self.run_query(query)
        return result[0][0] or 0.0 if result else 0.0