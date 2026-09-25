# Databricks notebook source
# MAGIC %md
# MAGIC # Pipeline ETL: Supabase Storage -> Delta Lake
# MAGIC
# MAGIC Extrai arquivos parquet do Supabase Storage e carrega como tabelas
# MAGIC Delta na camada Bronze do catálogo.

# COMMAND ----------

import logging
import sys

sys.path.append("/Workspace/Repos/SEU_USUARIO/supabase-databricks-etl")  # ajuste o path do repo

from src.config import validate_config
from src.extract import extract_parquet
from src.load import load_to_delta

logging.basicConfig(level=logging.INFO)
validate_config()

# COMMAND ----------

# Mapeamento: arquivo de origem -> tabela destino
TABELAS = {
    "clientes.parquet": "projetoecommerce.bronze.clientes",
    "pedidos.parquet": "projetoecommerce.bronze.pedidos",
    "produtos.parquet": "projetoecommerce.bronze.produtos",
    # adicione as demais tabelas extraídas do Supabase aqui
}

# COMMAND ----------

resultados = []

for key, tabela_destino in TABELAS.items():
    try:
        df = extract_parquet(key)
        load_to_delta(df, tabela_destino, spark)
        resultados.append({"tabela": tabela_destino, "linhas": len(df), "status": "OK"})
    except Exception as e:
        resultados.append({"tabela": tabela_destino, "linhas": 0, "status": f"ERRO: {e}"})

# COMMAND ----------

import pandas as pd

display(pd.DataFrame(resultados))
