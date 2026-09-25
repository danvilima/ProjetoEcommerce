"""
Carga de DataFrames pandas em tabelas Delta no Databricks.

Requer uma sessão Spark ativa (disponível automaticamente como `spark`
dentro de notebooks Databricks).
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def load_to_delta(
    df_pandas: pd.DataFrame,
    table_name: str,
    spark,
    mode: str = "overwrite",
) -> None:
    """
    Converte um DataFrame pandas para Spark e salva como tabela Delta.

    Args:
        df_pandas: DataFrame pandas de origem.
        table_name: nome completo da tabela destino
                    (ex: "catalogo.schema.tabela").
        spark: sessão SparkSession ativa.
        mode: modo de escrita ("overwrite", "append", etc).
    """
    df_spark = spark.createDataFrame(df_pandas)
    df_spark.write.format("delta").mode(mode).saveAsTable(table_name)
    logger.info(
        "Tabela '%s' carregada com sucesso (%d linhas, mode='%s')",
        table_name,
        df_pandas.shape[0],
        mode,
    )
