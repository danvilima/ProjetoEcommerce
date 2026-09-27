# Coletas repetidas podem distorcer a comparação; a mais recente por produto e concorrente
# é mantida. Um sinalizador de plausibilidade deixa preços excepcionalmente baixos visíveis.
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


@dp.materialized_view(name="preco_competidores")
@dp.expect_all_or_fail({"id_produto_preenchido": "id_produto IS NOT NULL", "preco_concorrente_positivo": "preco_concorrente > 0"})
@dp.expect("preco_plausivel", "preco_plausivel = true")
def preco_competidores():
    bronze = spark.read.table("bronze.preco_competirdores")
    dados = bronze.withColumn("__data_coleta", F.to_timestamp("data_coleta"))
    desempate = [F.col(c).asc_nulls_last() for c in bronze.columns if c != "data_coleta"]
    janela = Window.partitionBy("id_produto", "nome_concorrente").orderBy(F.col("__data_coleta").desc_nulls_last(), *desempate)
    dados = (dados.withColumn("__ordem", F.row_number().over(janela))
        .filter(F.col("__ordem") == 1).drop("__ordem", "data_coleta")
        .withColumnRenamed("__data_coleta", "data_coleta")
        .withColumn("preco_concorrente", F.col("preco_concorrente").cast("DECIMAL(10,2)")))
    produtos = spark.read.table("silver.produtos").select("id_produto", F.col("preco_atual").alias("__preco_atual"))
    comparados = dados.join(produtos, on="id_produto", how="left")
    suspeito = F.col("preco_concorrente") < F.col("__preco_atual") * F.lit(0.60)
    return (comparados.withColumn("preco_suspeito", F.coalesce(suspeito, F.lit(False)))
        .withColumn("preco_plausivel", ~F.col("preco_suspeito")).drop("__preco_atual"))
