-- Esta visão mantém uma linha por venda para análises que cruzam diretorias e filtros de dashboard.
-- Os dados cobrem 13/12/2025 a 11/01/2026; vendas sem produto cadastrado permanecem na tabela.
CREATE OR REFRESH MATERIALIZED VIEW gold.vendas_detalhadas (
  id_venda STRING COMMENT 'Identificador único da venda conforme silver.vendas.',
  data_venda TIMESTAMP COMMENT 'Data e hora originais da venda conforme silver.vendas.',
  data DATE COMMENT 'Data da venda, sem componente de hora, no período de 13/12/2025 a 11/01/2026.',
  dia_semana STRING COMMENT 'Nome do dia da semana em português, derivado da data da venda.',
  dia_semana_num INT COMMENT 'Número do dia da semana conforme silver.vendas; domingo = 1 e sábado = 7.',
  hora INT COMMENT 'Hora do dia da venda, entre 0 e 23.',
  canal_venda STRING COMMENT 'Canal em que a venda foi realizada.',
  id_produto STRING COMMENT 'Identificador do produto vendido, inclusive quando não existe cadastro.',
  nome_produto STRING COMMENT 'Nome cadastrado do produto ou Produto não cadastrado quando ausente.',
  categoria STRING COMMENT 'Categoria cadastrada do produto ou Não cadastrado quando ausente.',
  marca STRING COMMENT 'Marca cadastrada do produto ou Não cadastrado quando ausente.',
  faixa_preco STRING COMMENT 'Faixa do preço atual do produto (BASICO, MEDIO ou PREMIUM) ou Não cadastrado quando ausente.',
  produto_cadastrado BOOLEAN COMMENT 'Indica se o produto da venda existe em silver.produtos.',
  id_cliente STRING COMMENT 'Identificador do cliente que realizou a venda.',
  nome_cliente STRING COMMENT 'Nome do cliente sem pronome de tratamento, conforme silver.clientes.',
  estado STRING COMMENT 'Sigla da unidade federativa do cliente.',
  regiao STRING COMMENT 'Região do Brasil correspondente à unidade federativa do cliente.',
  segmento_cliente STRING COMMENT 'Segmento de Customer Success do cliente, conforme gold.clientes_segmentacao.',
  quantidade BIGINT COMMENT 'Quantidade de itens vendidos nesta venda.',
  preco_unitario DECIMAL(10,2) COMMENT 'Preço unitário em R$ registrado para a venda.',
  receita DECIMAL(10,2) COMMENT 'Receita desta venda em R$, conforme silver.vendas; não exclui produto não cadastrado.',
  venda_antes_do_cadastro BOOLEAN COMMENT 'Indica se a venda ocorreu antes da data de cadastro do produto; vendas sem data de cadastro são marcadas como false.'
)
CLUSTER BY (data)
COMMENT 'Detalhe de cada venda no período de 13/12/2025 a 11/01/2026, enriquecido com produto, cliente, região e segmento. Use para perguntas que cruzam diretorias e filtros; cada id_venda aparece uma vez e todas as vendas compõem a receita.'
AS
SELECT
  v.id_venda,
  v.data_venda,
  v.data,
  v.dia_semana,
  v.dia_semana_num,
  v.hora,
  v.canal_venda,
  v.id_produto,
  CASE WHEN p.id_produto IS NULL THEN 'Produto não cadastrado' ELSE p.nome_produto END AS nome_produto,
  CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.categoria END AS categoria,
  CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.marca END AS marca,
  CASE WHEN p.id_produto IS NULL THEN 'Não cadastrado' ELSE p.faixa_preco END AS faixa_preco,
  v.produto_cadastrado,
  v.id_cliente,
  c.nome_cliente,
  c.estado,
  c.regiao,
  c.segmento_cliente,
  v.quantidade,
  v.preco_unitario,
  v.receita,
  v.venda_antes_do_cadastro
FROM silver.vendas AS v
LEFT JOIN silver.produtos AS p
  ON v.id_produto = p.id_produto
LEFT JOIN gold.clientes_segmentacao AS c
  ON v.id_cliente = c.id_cliente;
