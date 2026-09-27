-- Esta visão consolida vendas por dia, hora e canal para analisar tendências e desempenho.
-- Os dados cobrem 13/12/2025 a 11/01/2026. Todas as vendas contam, mesmo sem produto cadastrado.
CREATE OR REFRESH MATERIALIZED VIEW gold.vendas_temporais (
  data DATE COMMENT 'Data da venda no período de 13/12/2025 a 11/01/2026.',
  dia_semana STRING COMMENT 'Nome do dia da semana em português, derivado da data da venda.',
  dia_semana_num INT COMMENT 'Número do dia da semana conforme silver.vendas; domingo = 1 e sábado = 7.',
  hora INT COMMENT 'Hora do dia da venda, entre 0 e 23, conforme silver.vendas.',
  canal_venda STRING COMMENT 'Canal em que a venda foi realizada, conforme silver.vendas.',
  total_vendas BIGINT NOT NULL COMMENT 'Quantidade de vendas no grupo data × hora × canal; cada linha de silver.vendas conta uma venda.',
  itens_vendidos BIGINT COMMENT 'Quantidade total de itens vendidos no grupo, soma de silver.vendas.quantidade.',
  receita DECIMAL(10,2) COMMENT 'Receita total do grupo em R$, soma de silver.vendas.receita; inclui vendas de produtos não cadastrados.',
  clientes_unicos BIGINT NOT NULL COMMENT 'Quantidade distinta de clientes no grupo. Não some este valor entre linhas; para clientes únicos compradores no período, consulte gold.clientes_segmentacao com total_compras > 0.'
)
COMMENT 'Vendas agregadas por data, hora e canal no período de 13/12/2025 a 11/01/2026. Use para tendências temporais e comparação de canais; clientes_unicos é uma métrica distinta por grupo e não pode ser somada entre grupos.'
AS
SELECT
  data,
  dia_semana,
  dia_semana_num,
  hora,
  canal_venda,
  COUNT(*) AS total_vendas,
  CAST(SUM(quantidade) AS BIGINT) AS itens_vendidos,
  CAST(SUM(receita) AS DECIMAL(10,2)) AS receita,
  COUNT(DISTINCT id_cliente) AS clientes_unicos
FROM silver.vendas
GROUP BY data, dia_semana, dia_semana_num, hora, canal_venda;
