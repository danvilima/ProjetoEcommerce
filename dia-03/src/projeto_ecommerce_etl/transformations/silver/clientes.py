# O nome original é preservado para auditoria; a versão normalizada remove tratamentos
# comuns e padroniza a capitalização. O mapa local evita depender de uma dimensão ausente.
from pyspark import pipelines as dp
from pyspark.sql import Window
from pyspark.sql import functions as F


UF_ESTADO_REGIAO = {
    "AC": ("Acre", "Norte"), "AL": ("Alagoas", "Nordeste"),
    "AP": ("Amapá", "Norte"), "AM": ("Amazonas", "Norte"),
    "BA": ("Bahia", "Nordeste"), "CE": ("Ceará", "Nordeste"),
    "DF": ("Distrito Federal", "Centro-Oeste"), "ES": ("Espírito Santo", "Sudeste"),
    "GO": ("Goiás", "Centro-Oeste"), "MA": ("Maranhão", "Nordeste"),
    "MT": ("Mato Grosso", "Centro-Oeste"), "MS": ("Mato Grosso do Sul", "Centro-Oeste"),
    "MG": ("Minas Gerais", "Sudeste"), "PA": ("Pará", "Norte"),
    "PB": ("Paraíba", "Nordeste"), "PR": ("Paraná", "Sul"),
    "PE": ("Pernambuco", "Nordeste"), "PI": ("Piauí", "Nordeste"),
    "RJ": ("Rio de Janeiro", "Sudeste"), "RN": ("Rio Grande do Norte", "Nordeste"),
    "RS": ("Rio Grande do Sul", "Sul"), "RO": ("Rondônia", "Norte"),
    "RR": ("Roraima", "Norte"), "SC": ("Santa Catarina", "Sul"),
    "SP": ("São Paulo", "Sudeste"), "SE": ("Sergipe", "Nordeste"),
    "TO": ("Tocantins", "Norte"),
}


@dp.materialized_view(name="clientes")
@dp.expect("nome_sem_pronome", "pronome_tratamento = false")
@dp.expect_all_or_fail({"id_cliente_preenchido": "id_cliente IS NOT NULL", "regiao_preenchida": "regiao IS NOT NULL"})
def clientes():
    bronze = spark.read.table("bronze.clientes")
    desempate = [F.col(c).asc_nulls_last() for c in bronze.columns if c != "data_cadastro"]
    janela = Window.partitionBy("id_cliente").orderBy(F.col("data_cadastro").desc_nulls_last(), *desempate)
    dados = (bronze.withColumn("__ordem", F.row_number().over(janela))
        .filter(F.col("__ordem") == 1).drop("__ordem")
        .withColumnRenamed("nome_cliente", "nome_original")
        .withColumn("estado", F.upper(F.trim("estado"))))
    tratamento = r"(?i)^\s*(Srta\.?|Sra\.?|Sr\.?|Dra\.?|Dr\.?)\s+"
    dados = dados.withColumn("pronome_tratamento", F.coalesce(F.col("nome_original").rlike(tratamento), F.lit(False)))
    dados = dados.withColumn("nome_cliente",
        F.initcap(F.trim(F.regexp_replace("nome_original", tratamento, ""))))
    mapa_uf = F.create_map(*[F.lit(item) for uf, (nome, _) in UF_ESTADO_REGIAO.items() for item in (uf, nome)])
    mapa_regiao = F.create_map(*[F.lit(item) for uf, (_, regiao) in UF_ESTADO_REGIAO.items() for item in (uf, regiao)])
    return dados.withColumn("nome_estado", mapa_uf[F.col("estado")]).withColumn("regiao", mapa_regiao[F.col("estado")])

