-- ====================================================================
-- PROJETO E-COMMERCE - DIA 1
-- Análise Exploratória de Dados (EDA) via Databricks SQL
-- Camada: Bronze
-- ====================================================================

-- 1. Exploração da base de clientes
-- --------------------------------------------------------------------
SELECT 
    nome_cliente
FROM projetoecommerce.bronze.clientes;

-- Clientes situados no RJ
SELECT 
    nome_cliente,
    estado
FROM projetoecommerce.bronze.clientes
WHERE estado = 'RJ';

-- Clientes situados fora do RJ
SELECT 
    nome_cliente,
    estado
FROM projetoecommerce.bronze.clientes
WHERE estado != 'RJ';


-- 2. Análise de pedidos individuais
-- --------------------------------------------------------------------
-- Cálculo de receita por transação
SELECT
    id_venda,
    (quantidade * preco_unitario) AS total_de_vendas
FROM projetoecommerce.bronze.vendas;

-- Top 10 maiores pedidos no geral
SELECT
    id_venda,
    (quantidade * preco_unitario) AS total_de_vendas
FROM projetoecommerce.bronze.vendas
ORDER BY total_de_vendas DESC
LIMIT 10;

-- Top 10 maiores transações de loja física com quantidade < 3
SELECT
    id_venda,
    canal_venda,
    quantidade,
    preco_unitario,
    (quantidade * preco_unitario) AS receita
FROM projetoecommerce.bronze.vendas
WHERE canal_venda = 'loja_fisica'
  AND quantidade < 3
ORDER BY receita DESC
LIMIT 10;


-- 3. Métricas agregadas e KPIs de negócio
-- --------------------------------------------------------------------
-- Métricas gerais consolidadas
SELECT
    SUM(quantidade * preco_unitario) AS receita_total,
    ROUND(AVG(quantidade * preco_unitario), 2) AS ticket_medio,
    COUNT(*) AS total_pedidos,
    MIN(quantidade * preco_unitario) AS menor_venda,
    MAX(quantidade * preco_unitario) AS maior_venda
FROM projetoecommerce.bronze.vendas;

-- Métricas segmentadas por canal de venda
SELECT
    canal_venda,
    SUM(quantidade * preco_unitario) AS receita_total,
    ROUND(AVG(quantidade * preco_unitario), 2) AS ticket_medio,
    COUNT(*) AS total_pedidos,
    MIN(quantidade * preco_unitario) AS menor_venda,
    MAX(quantidade * preco_unitario) AS maior_venda
FROM projetoecommerce.bronze.vendas
GROUP BY canal_venda
ORDER BY receita_total DESC;

-- Receita consolidada por estado (Cruzamento Clientes x Vendas)
SELECT
    c.estado,
    COUNT(v.id_venda) AS total_pedidos,
    SUM(v.quantidade * v.preco_unitario) AS total_receita
FROM projetoecommerce.bronze.vendas AS v
INNER JOIN projetoecommerce.bronze.clientes AS c 
    ON v.id_cliente = c.id_cliente
GROUP BY c.estado
ORDER BY total_receita DESC;