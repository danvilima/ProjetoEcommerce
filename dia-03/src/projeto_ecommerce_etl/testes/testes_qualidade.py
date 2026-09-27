# Databricks notebook source
# As verificações protegem as chaves e a receita da silver sem remover registros válidos.
dbutils.widgets.text("catalogo", "projetoecommerce")
catalogo = dbutils.widgets.get("catalogo")

# COMMAND ----------

from pyspark.sql import Row


def contar(sql):
    return int(spark.sql(sql).first()[0])


verificacoes = [
    ("chave_unica_produtos",
     f"SELECT COUNT(*) FROM (SELECT id_produto FROM {catalogo}.silver.produtos GROUP BY id_produto HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("chave_unica_clientes",
     f"SELECT COUNT(*) FROM (SELECT id_cliente FROM {catalogo}.silver.clientes GROUP BY id_cliente HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("chave_unica_preco_competidores",
     f"SELECT COUNT(*) FROM (SELECT id_produto, nome_concorrente FROM {catalogo}.silver.preco_competidores GROUP BY id_produto, nome_concorrente HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("chave_unica_vendas",
     f"SELECT COUNT(*) FROM (SELECT id_venda FROM {catalogo}.silver.vendas GROUP BY id_venda HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("receita_consistente",
     f"SELECT COUNT(*) FROM {catalogo}.silver.vendas WHERE receita IS NULL OR receita <> CAST(quantidade * preco_unitario AS DECIMAL(10,2))",
     0, "maximo"),
    ("vendas_sem_produto_cadastrado",
     f"SELECT COUNT(*) FROM {catalogo}.silver.vendas WHERE produto_cadastrado = false",
     0.01, "fracao_maxima_exclusiva"),
    ("clientes_segmentacao_receita_igual_silver",
     f"SELECT CASE WHEN (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.gold.clientes_segmentacao) = (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.silver.vendas) THEN 0 ELSE 1 END",
     0, "maximo"),
    ("clientes_segmentacao_id_unico",
     f"SELECT COUNT(*) FROM (SELECT id_cliente FROM {catalogo}.gold.clientes_segmentacao GROUP BY id_cliente HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("clientes_segmentacao_valores_validos",
     f"SELECT COUNT(*) FROM {catalogo}.gold.clientes_segmentacao WHERE segmento_cliente NOT IN ('VIP', 'TOP_TIER', 'REGULAR') OR segmento_cliente IS NULL",
     0, "maximo"),
    ("clientes_segmentacao_vip_minimo",
     f"SELECT COUNT(*) FROM {catalogo}.gold.clientes_segmentacao WHERE segmento_cliente = 'VIP' AND receita < 22000",
     0, "maximo"),
    ("clientes_segmentacao_comentarios_colunas",
     f"SELECT COUNT(*) FROM {catalogo}.information_schema.columns WHERE table_catalog = '{catalogo}' AND table_schema = 'gold' AND NOT startswith(table_name, '__materialization') AND (comment IS NULL OR TRIM(comment) = '')",
     0, "maximo"),
    ("clientes_segmentacao_quantidade_clientes",
     f"SELECT CASE WHEN COUNT(*) = 50 THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao",
     0, "maximo"),
    ("clientes_segmentacao_total_vips",
     f"SELECT CASE WHEN COUNT(*) = 10 THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao WHERE segmento_cliente = 'VIP'",
     0, "maximo"),
    ("clientes_segmentacao_total_top_tier",
     f"SELECT CASE WHEN COUNT(*) = 25 THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao WHERE segmento_cliente = 'TOP_TIER'",
     0, "maximo"),
    ("clientes_segmentacao_total_regular",
     f"SELECT CASE WHEN COUNT(*) = 15 THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao WHERE segmento_cliente = 'REGULAR'",
     0, "maximo"),
    ("clientes_segmentacao_receita_esperada",
     f"SELECT CASE WHEN SUM(receita) = CAST(974077.28 AS DECIMAL(10,2)) THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao",
     0, "maximo"),
    ("clientes_segmentacao_maior_cliente_esperado",
     f"SELECT CASE WHEN COUNT(*) = 1 THEN 0 ELSE 1 END FROM {catalogo}.gold.clientes_segmentacao WHERE ranking_receita = 1 AND nome_cliente = 'Ana Sophia Pereira' AND estado = 'MG' AND receita = CAST(30716.63 AS DECIMAL(10,2))",
     0, "maximo"),
    ("vendas_temporais_receita_igual_silver",
     f"SELECT CASE WHEN (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.gold.vendas_temporais) = (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.silver.vendas) THEN 0 ELSE 1 END",
     0, "maximo"),
    ("vendas_produtos_receita_igual_silver",
     f"SELECT CASE WHEN (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.gold.vendas_produtos) = (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.silver.vendas) THEN 0 ELSE 1 END",
     0, "maximo"),
    ("vendas_detalhadas_receita_igual_silver",
     f"SELECT CASE WHEN (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.gold.vendas_detalhadas) = (SELECT COALESCE(SUM(receita), CAST(0 AS DECIMAL(10,2))) FROM {catalogo}.silver.vendas) THEN 0 ELSE 1 END",
     0, "maximo"),
    ("vendas_silver_quantidade_esperada",
     f"SELECT CASE WHEN COUNT(*) = 3020 THEN 0 ELSE 1 END FROM {catalogo}.silver.vendas",
     0, "maximo"),
    ("vendas_temporais_quantidade_esperada",
     f"SELECT CASE WHEN SUM(total_vendas) = 3020 THEN 0 ELSE 1 END FROM {catalogo}.gold.vendas_temporais",
     0, "maximo"),
    ("vendas_temporais_ecommerce_esperado",
     f"SELECT CASE WHEN SUM(total_vendas) = 2155 THEN 0 ELSE 1 END FROM {catalogo}.gold.vendas_temporais WHERE canal_venda = 'ecommerce'",
     0, "maximo"),
    ("vendas_produtos_quantidade_esperada",
     f"SELECT CASE WHEN SUM(total_vendas) = 3020 THEN 0 ELSE 1 END FROM {catalogo}.gold.vendas_produtos",
     0, "maximo"),
    ("vendas_produtos_id_unico",
     f"SELECT COUNT(*) FROM (SELECT id_produto FROM {catalogo}.gold.vendas_produtos GROUP BY id_produto HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("vendas_detalhadas_quantidade_esperada",
     f"SELECT CASE WHEN COUNT(*) = 3020 THEN 0 ELSE 1 END FROM {catalogo}.gold.vendas_detalhadas",
     0, "maximo"),
    ("vendas_detalhadas_id_unico",
     f"SELECT COUNT(*) FROM (SELECT id_venda FROM {catalogo}.gold.vendas_detalhadas GROUP BY id_venda HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("vendas_detalhadas_cliente_com_segmento_e_regiao",
     f"SELECT COUNT(*) FROM {catalogo}.gold.vendas_detalhadas WHERE segmento_cliente IS NULL OR regiao IS NULL",
     0, "maximo"),
    ("precos_competitividade_id_produto_unico",
     f"SELECT COUNT(*) FROM (SELECT id_produto FROM {catalogo}.gold.precos_competitividade GROUP BY id_produto HAVING COUNT(*) > 1)",
     0, "maximo"),
    ("precos_competitividade_total_produtos",
     f"SELECT CASE WHEN COUNT(*) = 215 THEN 0 ELSE 1 END FROM {catalogo}.gold.precos_competitividade",
     0, "maximo"),
    ("precos_competitividade_mais_caro_que_todos",
     f"SELECT CASE WHEN COUNT(*) = 35 THEN 0 ELSE 1 END FROM {catalogo}.gold.precos_competitividade WHERE classificacao_preco = 'MAIS_CARO_QUE_TODOS'",
     0, "maximo"),
    ("precos_competitividade_precos_suspeitos",
     f"SELECT CASE WHEN COUNT(*) = 15 THEN 0 ELSE 1 END FROM {catalogo}.gold.precos_competitividade WHERE possui_preco_suspeito = true",
     0, "maximo"),
]

# COMMAND ----------

resultados = []
for nome, consulta, limite, tipo_limite in verificacoes:
    problemas = contar(consulta)
    if tipo_limite == "fracao_maxima_exclusiva":
        total = contar(f"SELECT COUNT(*) FROM {catalogo}.silver.vendas")
        proporcao = problemas / total if total else 0.0
        passou = proporcao < limite
        detalhe = f"{proporcao:.4%} do total (limite exclusivo: 1%)"
    else:
        passou = problemas <= limite
        detalhe = f"limite: {limite}"
    resultados.append(Row(teste=nome, linhas_com_problema=problemas, limite=detalhe, passou=passou))

tabela_resultados = spark.createDataFrame(resultados)
display(tabela_resultados)

falhas = [linha.teste for linha in resultados if not linha.passou]
if falhas:
    raise AssertionError("Testes de qualidade falharam: " + ", ".join(falhas))
