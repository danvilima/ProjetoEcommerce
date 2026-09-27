-- A comparação usa somente Mercado Livre, Amazon, Magalu e Shopee, conforme o escopo comercial.
-- Preços suspeitos podem refletir promoções reais; permanecem em todas as contas e são sinalizados.
-- Os dados de referência cobrem o período de 13/12/2025 a 11/01/2026.
CREATE OR REFRESH MATERIALIZED VIEW gold.precos_competitividade (
  id_produto STRING COMMENT 'Identificador único do produto; use este campo para comparar e contar produtos.',
  nome_produto STRING COMMENT 'Nome do produto conforme silver.produtos.',
  categoria STRING COMMENT 'Categoria do produto conforme silver.produtos.',
  marca STRING COMMENT 'Marca do produto conforme silver.produtos.',
  nosso_preco DECIMAL(10,2) COMMENT 'Preço atual praticado por nós em R$, conforme silver.produtos.preco_atual.',
  preco_medio_concorrentes DECIMAL(10,2) COMMENT 'Média em R$ dos preços disponíveis de Mercado Livre, Amazon, Magalu e Shopee, arredondada para duas casas; inclui preços suspeitos.',
  preco_minimo_concorrentes DECIMAL(10,2) COMMENT 'Menor preço em R$ disponível entre os quatro concorrentes considerados; inclui preços suspeitos.',
  preco_maximo_concorrentes DECIMAL(10,2) COMMENT 'Maior preço em R$ disponível entre os quatro concorrentes considerados; inclui preços suspeitos.',
  total_concorrentes BIGINT NOT NULL COMMENT 'Quantidade de concorrentes com preço disponível para o produto, dentre Mercado Livre, Amazon, Magalu e Shopee.',
  diferenca_pct_vs_media DECIMAL(10,2) COMMENT 'Diferença percentual de nosso preço para a média: (nosso_preco - preco_medio_concorrentes) / preco_medio_concorrentes × 100, arredondada a duas casas; 10 significa 10% mais caro e valor negativo significa mais barato.',
  diferenca_pct_vs_minimo DECIMAL(10,2) COMMENT 'Diferença percentual de nosso preço para o menor preço: (nosso_preco - preco_minimo_concorrentes) / preco_minimo_concorrentes × 100, arredondada a duas casas; 10 significa 10% mais caro e valor negativo significa mais barato.',
  classificacao_preco STRING NOT NULL COMMENT 'Classificação em ordem de prioridade: MAIS_CARO_QUE_TODOS se nosso preço supera o maior; MAIS_BARATO_QUE_TODOS se fica abaixo do menor; senão ACIMA_DA_MEDIA, ABAIXO_DA_MEDIA ou NA_MEDIA por comparação com a média arredondada.',
  possui_preco_suspeito BOOLEAN NOT NULL COMMENT 'Indica se pelo menos um preço concorrente está marcado como suspeito em silver.preco_competidores. O preço suspeito permanece na média, nos mínimos, máximos e na classificação; confirme se é promoção real antes de agir.',
  receita DECIMAL(10,2) NOT NULL COMMENT 'Receita do produto em R$, soma de silver.vendas.receita; produtos sem venda recebem R$ 0,00.',
  itens_vendidos BIGINT NOT NULL COMMENT 'Quantidade de itens vendidos, soma de silver.vendas.quantidade; produtos sem venda recebem 0.'
)
COMMENT 'Compara o preço atual dos produtos com os preços disponíveis de Mercado Livre, Amazon, Magalu e Shopee, usando os dados do período de 13/12/2025 a 11/01/2026. Use para priorizar ações de Pricing. Preços suspeitos permanecem nas métricas porque podem representar promoções relâmpago; confira possui_preco_suspeito antes de reagir.'
AS
WITH concorrentes_agregados AS (
  SELECT
    id_produto,
    CAST(ROUND(AVG(preco_concorrente), 2) AS DECIMAL(10,2)) AS preco_medio_concorrentes,
    MIN(preco_concorrente) AS preco_minimo_concorrentes,
    MAX(preco_concorrente) AS preco_maximo_concorrentes,
    COUNT(*) AS total_concorrentes,
    COALESCE(MAX(CASE WHEN preco_suspeito THEN 1 ELSE 0 END), 0) = 1 AS possui_preco_suspeito
  FROM silver.preco_competidores
  WHERE UPPER(TRIM(nome_concorrente)) IN ('MERCADO LIVRE', 'AMAZON', 'MAGALU', 'SHOPEE')
  GROUP BY id_produto
), vendas_agregadas AS (
  SELECT
    id_produto,
    CAST(SUM(receita) AS DECIMAL(10,2)) AS receita,
    CAST(SUM(quantidade) AS BIGINT) AS itens_vendidos
  FROM silver.vendas
  GROUP BY id_produto
), produtos_comparados AS (
  SELECT
    p.id_produto,
    p.nome_produto,
    p.categoria,
    p.marca,
    p.preco_atual AS nosso_preco,
    c.preco_medio_concorrentes,
    c.preco_minimo_concorrentes,
    c.preco_maximo_concorrentes,
    c.total_concorrentes,
    CAST(ROUND((p.preco_atual - c.preco_medio_concorrentes) / c.preco_medio_concorrentes * 100, 2) AS DECIMAL(10,2)) AS diferenca_pct_vs_media,
    CAST(ROUND((p.preco_atual - c.preco_minimo_concorrentes) / c.preco_minimo_concorrentes * 100, 2) AS DECIMAL(10,2)) AS diferenca_pct_vs_minimo,
    CASE
      WHEN p.preco_atual > c.preco_maximo_concorrentes THEN 'MAIS_CARO_QUE_TODOS'
      WHEN p.preco_atual < c.preco_minimo_concorrentes THEN 'MAIS_BARATO_QUE_TODOS'
      WHEN p.preco_atual > c.preco_medio_concorrentes THEN 'ACIMA_DA_MEDIA'
      WHEN p.preco_atual < c.preco_medio_concorrentes THEN 'ABAIXO_DA_MEDIA'
      ELSE 'NA_MEDIA'
    END AS classificacao_preco,
    c.possui_preco_suspeito,
    COALESCE(v.receita, CAST(0 AS DECIMAL(10,2))) AS receita,
    COALESCE(v.itens_vendidos, CAST(0 AS BIGINT)) AS itens_vendidos
  FROM silver.produtos AS p
  INNER JOIN concorrentes_agregados AS c
    ON p.id_produto = c.id_produto
  LEFT JOIN vendas_agregadas AS v
    ON p.id_produto = v.id_produto
)
SELECT
  id_produto,
  nome_produto,
  categoria,
  marca,
  nosso_preco,
  preco_medio_concorrentes,
  preco_minimo_concorrentes,
  preco_maximo_concorrentes,
  total_concorrentes,
  diferenca_pct_vs_media,
  diferenca_pct_vs_minimo,
  classificacao_preco,
  possui_preco_suspeito,
  receita,
  itens_vendidos
FROM produtos_comparados;
