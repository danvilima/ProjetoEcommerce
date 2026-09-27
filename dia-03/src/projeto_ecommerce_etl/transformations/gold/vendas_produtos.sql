-- Esta visão permite comparar desempenho por produto cadastrado sem ocultar vendas sem dimensão.
-- Os dados cobrem 13/12/2025 a 11/01/2026; nomes iguais podem pertencer a IDs de produto diferentes.
CREATE OR REFRESH MATERIALIZED VIEW gold.vendas_produtos (
  id_produto STRING COMMENT 'Identificador do produto; use este campo para contar produtos distintos.',
  nome_produto STRING COMMENT 'Nome do produto. Produtos distintos podem compartilhar o mesmo nome; agrupe por id_produto. Sem cadastro, recebe Produto não cadastrado.',
  categoria STRING COMMENT 'Categoria cadastrada do produto; sem cadastro, recebe Não cadastrado.',
  marca STRING COMMENT 'Marca cadastrada do produto; sem cadastro, recebe Não cadastrado.',
  faixa_preco STRING COMMENT 'Faixa do preço atual do produto (BASICO, MEDIO ou PREMIUM); sem cadastro, recebe Não cadastrado.',
  produto_cadastrado BOOLEAN COMMENT 'Indica se o produto da venda existe em silver.produtos.',
  total_vendas BIGINT NOT NULL COMMENT 'Quantidade de vendas do produto no período de 13/12/2025 a 11/01/2026; cada linha de silver.vendas conta uma venda.',
  itens_vendidos BIGINT COMMENT 'Quantidade total de itens vendidos do produto, soma de silver.vendas.quantidade.',
  receita DECIMAL(10,2) COMMENT 'Receita do produto em R$, soma de silver.vendas.receita; inclui vendas sem cadastro de produto.',
  ticket_medio DECIMAL(10,2) COMMENT 'Ticket médio por venda do produto em R$, média de silver.vendas.receita arredondada para duas casas.',
  ranking_receita BIGINT NOT NULL COMMENT 'Posição única do produto por receita decrescente entre todos os produtos; empates são desempatados por id_produto crescente.',
  ranking_na_categoria BIGINT NOT NULL COMMENT 'Posição única por receita decrescente dentro da categoria; empates são desempatados por id_produto crescente.'
)
COMMENT 'Desempenho agregado por produto no período de 13/12/2025 a 11/01/2026. Cada produto é identificado por id_produto, pois nomes podem se repetir. A receita inclui vendas de produtos não cadastrados, agrupadas pelo id_produto da venda.'
AS
WITH vendas_com_produto AS (
  SELECT
    v.id_venda,
    v.id_produto,
    CASE WHEN p.id_produto IS NULL THEN 'Produto não cadastrado' ELSE p.nome_produto END AS nome_produto,
    CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.categoria END AS categoria,
    CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.marca END AS marca,
    CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.faixa_preco END AS faixa_preco,
    v.produto_cadastrado,
    v.quantidade,
    v.receita
  FROM silver.vendas AS v
  LEFT JOIN silver.produtos AS p
    ON v.id_produto = p.id_produto
), produtos_agregados AS (
  SELECT
    id_produto,
    nome_produto,
    categoria,
    marca,
    faixa_preco,
    produto_cadastrado,
    COUNT(*) AS total_vendas,
    CAST(SUM(quantidade) AS BIGINT) AS itens_vendidos,
    CAST(SUM(receita) AS DECIMAL(10,2)) AS receita,
    CAST(ROUND(AVG(receita), 2) AS DECIMAL(10,2)) AS ticket_medio
  FROM vendas_com_produto
  GROUP BY id_produto, nome_produto, categoria, marca, faixa_preco, produto_cadastrado
)
SELECT
  id_produto,
  nome_produto,
  categoria,
  marca,
  faixa_preco,
  produto_cadastrado,
  total_vendas,
  itens_vendidos,
  receita,
  ticket_medio,
  CAST(ROW_NUMBER() OVER (ORDER BY receita DESC, id_produto ASC) AS BIGINT) AS ranking_receita,
  CAST(ROW_NUMBER() OVER (PARTITION BY categoria ORDER BY receita DESC, id_produto ASC) AS BIGINT) AS ranking_na_categoria
FROM produtos_agregados;
