# 📊 Dia 1: Análise Exploratória de Dados (EDA) com Databricks SQL

## 🎯 Objetivo do Dia
Iniciar o projeto de Engenharia e Análise de Dados explorando a camada **Bronze** (dados brutos ingeridos) de um ecossistema de E-commerce. O foco foi responder a perguntas de negócio diretamente no lakehouse via **Databricks SQL / Unity Catalog**, sem necessidade de movimentação externa de dados.

---

## 🗺️ Contexto no Roadmap do Projeto
Conforme o planejamento da arquitetura ponta a ponta:
- 📍 **[Você está aqui] Dia 1:** EDA e Perguntas de Negócio via SQL direto no Lakehouse
- ⏳ **Dia 2:** Ingestão de Dados (Extract & Load com Python e orquestração)
- ⏳ **Dia 3:** Transformação e Modelagem (Lakeflow, dbt/PySpark, Camadas Bronze/Silver/Gold)
- ⏳ **Dia 4:** Data Apps, Agentes de IA e consumo analítico

---

## 🗄️ Estrutura das Tabelas (Camada Bronze)

* **`projetoecommerce.bronze.clientes`**: Cadastro de clientes (identificadores, nome, localização geográfica/UF).
* **`projetoecommerce.bronze.vendas`**: Transações de vendas (id da venda, id do cliente, canal de venda, quantidade e preço unitário).

---

## 💡 Perguntas de Negócio & Consultas Desenvolvidas

### 1. Perfil Demográfico dos Clientes

#### 1.1 Listagem Geral de Clientes
```sql
SELECT 
    nome_cliente
FROM projetoecommerce.bronze.clientes;
```

#### 1.2 Segmentação Regional (Filtro RJ vs. Outros Estados)
Identificação da base concentrada no estado do Rio de Janeiro e fora dele:
```sql
-- Clientes do RJ
SELECT 
    nome_cliente,
    estado
FROM projetoecommerce.bronze.clientes
WHERE estado = 'RJ';

-- Clientes fora do RJ
SELECT 
    nome_cliente,
    estado
FROM projetoecommerce.bronze.clientes
WHERE estado != 'RJ';
```

---

### 2. Análise de Transações e Receita Individual

#### 2.1 Cálculo do Valor Total por Transação
Cálculo da métrica derivada de faturamento por linha de venda:
```sql
SELECT
    id_venda,
    (quantidade * preco_unitario) AS total_venda
FROM projetoecommerce.bronze.vendas;
```

#### 2.2 Top 10 Maiores Vendas Gerais
```sql
SELECT
    id_venda,
    id_cliente,
    canal_venda,
    quantidade,
    preco_unitario,
    (quantidade * preco_unitario) AS receita_total
FROM projetoecommerce.bronze.vendas
ORDER BY receita_total DESC
LIMIT 10;
```

#### 2.3 Top 10 Maiores Vendas em Loja Física (com limite de volume)
Análise específica para o canal presencial avaliando tickets altos com volume de itens reduzido ($< 3$ unidades):
```sql
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
```

---

### 3. Agregações e KPIs Executivos

#### 3.1 Métricas Gerais da Operação
Visão macro de faturamento, ticket médio, volumetria e extremos de venda:
```sql
SELECT
    SUM(quantidade * preco_unitario) AS receita_total,
    ROUND(AVG(quantidade * preco_unitario), 2) AS ticket_medio,
    COUNT(*) AS total_pedidos,
    MIN(quantidade * preco_unitario) AS menor_venda,
    MAX(quantidade * preco_unitario) AS maior_venda
FROM projetoecommerce.bronze.vendas;
```

#### 3.2 Performance Comparativa por Canal de Venda
Avaliação do faturamento e comportamento de compra entre canais:
```sql
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
```

#### 3.3 Faturamento Consolidado por Estado (JOIN Clientes $\times$ Vendas)
Cruzamento relacional para identificar as praças mais rentáveis da operação:
```sql
SELECT
    c.estado,
    COUNT(v.id_venda) AS total_pedidos,
    SUM(v.quantidade * v.preco_unitario) AS faturamento_total
FROM projetoecommerce.bronze.vendas AS v
INNER JOIN projetoecommerce.bronze.clientes AS c 
    ON v.id_cliente = c.id_cliente
GROUP BY c.estado
ORDER BY faturamento_total DESC;
```

---

## 🧠 Principais Aprendizados e Habilidades Aplicadas
- **Databricks SQL & Unity Catalog:** Navegação e consulta direta em tabelas gerenciadas dentro da arquitetura de Lakehouse.
- **SQL DQL (Data Query Language):**
  - Projeções e expressões aritméticas calculadas no próprio `SELECT`.
  - Filtros lógicos simples e compostos (`WHERE`, `AND`, operadores de negação `!=`).
  - Ordenação e corte de dados analíticos (`ORDER BY`, `LIMIT`).
  - Funções de agregação (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`) combinadas com `GROUP BY`.
  - Relacionamento de conjuntos analíticos através de `INNER JOIN`.