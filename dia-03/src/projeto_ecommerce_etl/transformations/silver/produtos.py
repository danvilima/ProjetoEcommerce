# Produtos duplicados podem inflar joins; manter o registro mais recente torna a escolha
# determinística. O preço é convertido para centavos para padronizar comparações e receita.
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


@dp.materialized_view(name="produtos")
@dp.expect_all_or_fail({"id_produto_preenchido": "id_produto IS NOT NULL", "preco_atual_positivo": "preco_atual > 0"})
def produtos():
    bronze = spark.read.table("bronze.produtos")
    desempate = [F.col(c).asc_nulls_last() for c in bronze.columns if c != "data_criacao"]
    janela = Window.partitionBy("id_produto").orderBy(F.col("data_criacao").desc_nulls_last(), *desempate)
    dados = (bronze.withColumn("__ordem", F.row_number().over(janela))
        .filter(F.col("__ordem") == 1).drop("__ordem")
        .withColumn("nome_produto", F.trim("nome_produto"))
        .withColumn("preco_atual", F.col("preco_atual").cast("DECIMAL(10,2)")))
    return dados.withColumn("faixa_preco",
        F.when(F.col("preco_atual") > 1000, "PREMIUM")
         .when(F.col("preco_atual") > 500, "MEDIO").otherwise("BASICO"))
