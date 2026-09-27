-- A diretoria de Customer Success precisa priorizar clientes e ativar quem ainda não comprou.
-- Os limites foram definidos pela distribuição real: R$ 10.000 e R$ 5.000 tornavam quase
-- toda a carteira VIP e não separavam os melhores clientes de forma útil.
-- A receita inclui toda venda registrada em silver.vendas, mesmo sem produto cadastrado.
CREATE OR REFRESH MATERIALIZED VIEW gold.clientes_segmentacao (
  id_cliente STRING COMMENT 'Identificador único do cliente, conforme silver.clientes.',
  nome_cliente STRING COMMENT 'Nome do cliente sem pronome de tratamento, conforme silver.clientes.',
  estado STRING COMMENT 'Sigla da unidade federativa do cliente; não é o nome completo do estado.',
  nome_estado STRING COMMENT 'Nome por extenso da unidade federativa do cliente.',
  regiao STRING COMMENT 'Região do Brasil correspondente à unidade federativa do cliente.',
  total_compras BIGINT NOT NULL COMMENT 'Quantidade de vendas do cliente em silver.vendas; cada id_venda conta como uma compra.',
  receita DECIMAL(10,2) COMMENT 'Receita acumulada do cliente em R$, soma de silver.vendas.receita; inclui produtos não cadastrados e vale R$ 0,00 sem compras.',
  ticket_medio DECIMAL(10,2) COMMENT 'Ticket médio em R$, média da receita das vendas do cliente arredondada para duas casas; fica NULL sem compras.',
  primeira_compra DATE COMMENT 'Data da primeira venda do cliente; fica NULL sem compras.',
  ultima_compra DATE COMMENT 'Data da venda mais recente do cliente; fica NULL sem compras.',
  segmento_cliente STRING NOT NULL COMMENT 'Faixa definida pela receita acumulada: VIP a partir de R$ 22.000,00; TOP_TIER de R$ 17.000,00 a R$ 21.999,99; REGULAR abaixo de R$ 17.000,00.',
  ranking_receita BIGINT NOT NULL COMMENT 'Posição única do cliente por receita decrescente; em caso de empate, id_cliente crescente desempata.'
)
COMMENT 'Carteira completa para dashboard e Genie de Customer Success: uma linha por cliente, inclusive sem compras. Use receita para valor acumulado em R$, ticket_medio para média por venda e segmento_cliente para a faixa acordada. Vendas de produtos não cadastrados também compõem a receita.'
AS
WITH vendas_por_cliente AS (
  SELECT
    id_cliente,
    COUNT(id_venda) AS total_compras,
    CAST(SUM(receita) AS DECIMAL(10,2)) AS receita,
    CAST(ROUND(AVG(receita), 2) AS DECIMAL(10,2)) AS ticket_medio,
    MIN(data) AS primeira_compra,
    MAX(data) AS ultima_compra
  FROM silver.vendas
  GROUP BY id_cliente
), clientes_com_metricas AS (
  SELECT
    c.id_cliente,
    c.nome_cliente,
    c.estado,
    c.nome_estado,
    c.regiao,
    COALESCE(v.total_compras, CAST(0 AS BIGINT)) AS total_compras,
    COALESCE(v.receita, CAST(0 AS DECIMAL(10,2))) AS receita,
    v.ticket_medio,
    v.primeira_compra,
    v.ultima_compra
  FROM silver.clientes AS c
  LEFT JOIN vendas_por_cliente AS v
    ON c.id_cliente = v.id_cliente
)
SELECT
  id_cliente,
  nome_cliente,
  estado,
  nome_estado,
  regiao,
  total_compras,
  receita,
  ticket_medio,
  primeira_compra,
  ultima_compra,
  CASE
    WHEN receita >= 22000 THEN 'VIP'
    WHEN receita >= 17000 THEN 'TOP_TIER'
    ELSE 'REGULAR'
  END AS segmento_cliente,
  CAST(ROW_NUMBER() OVER (ORDER BY receita DESC, id_cliente ASC) AS BIGINT) AS ranking_receita
FROM clientes_com_metricas;
