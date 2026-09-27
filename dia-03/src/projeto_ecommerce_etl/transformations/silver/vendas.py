# As vendas não são descartadas: problemas conhecidos ficam marcados para auditoria sem
# alterar a receita. A leitura batch permite recalcular indicadores quando a bronze muda.
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


@dp.materialized_view(name="vendas")
@dp.expect_all_or_fail({
    "id_venda_preenchido": "id_venda IS NOT NULL",
    "data_venda_preenchida": "data_venda IS NOT NULL",
    "id_cliente_preenchido": "id_cliente IS NOT NULL",
    "id_produto_preenchido": "id_produto IS NOT NULL",
    "quantidade_preenchida_e_positiva": "quantidade IS NOT NULL AND quantidade > 0",
    "preco_unitario_preenchido_e_positivo": "preco_unitario IS NOT NULL AND preco_unitario > 0",
    "canal_venda_valido": "canal_venda IN ('ecommerce', 'loja_fisica')",
})
@dp.expect("produto_cadastrado", "produto_cadastrado = true")
@dp.expect("venda_depois_do_cadastro", "venda_depois_do_cadastro = true")
def vendas():
    bronze = spark.read.table("bronze.vendas")
    desempate = [F.col(c).asc_nulls_last() for c in bronze.columns if c != "data_venda"]
    janela = Window.partitionBy("id_venda").orderBy(F.col("data_venda").desc_nulls_last(), *desempate)
    dados = (bronze.withColumn("__ordem", F.row_number().over(janela))
        .filter(F.col("__ordem") == 1).drop("__ordem")
        .withColumn("preco_unitario", F.col("preco_unitario").cast("DECIMAL(10,2)")))
    produtos = spark.read.table("silver.produtos").select("id_produto", F.col("data_criacao").alias("__data_criacao"))
    dados = dados.join(produtos, on="id_produto", how="left")
    data_venda = F.col("data_venda")
    data_criacao = F.col("__data_criacao")
    dia_num = F.dayofweek(data_venda)
    dias = F.create_map(*[F.lit(item) for numero, nome in enumerate(
        ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"], start=1
    ) for item in (numero, nome)])
    antes = F.when(data_criacao.isNotNull(), data_venda < data_criacao).otherwise(False)
    return (dados
        .withColumn("receita", (F.col("quantidade") * F.col("preco_unitario")).cast("DECIMAL(10,2)"))
        .withColumn("data", F.to_date(data_venda))
        .withColumn("hora", F.hour(data_venda))
        .withColumn("dia_semana_num", dia_num)
        .withColumn("dia_semana", dias[dia_num])
        .withColumn("produto_cadastrado", F.col("__data_criacao").isNotNull())
        .withColumn("venda_antes_do_cadastro", antes)
        .withColumn("venda_depois_do_cadastro", ~F.col("venda_antes_do_cadastro"))
        .drop("__data_criacao"))
