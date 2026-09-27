# Esta visao historica e mantida para consumidores existentes; a receita vem da silver
# padronizada e conserva as colunas publicadas anteriormente.
from pyspark import pipelines as dp


@dp.materialized_view(name="receita_por_canal")
@dp.expect_all_or_fail({"receita_positiva": "receita > 0"})
def receita_por_canal():
    return spark.read.table("silver.vendas").select(
        "id_venda",
        "data_venda",
        "id_cliente",
        "id_produto",
        "canal_venda",
        "quantidade",
        "preco_unitario",
        "receita",
    )
