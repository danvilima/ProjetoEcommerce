# CLAUDE.md

Project guidance for AI agents lives in AGENTS.md.
Claude Code loads it via the import below.

@AGENTS.md

## Convencoes do projeto

- Use o catalogo projetoecommerce e os schemas bronze, silver e gold.
- Escreva nomes de tabelas e colunas em portugues, snake_case e sem acentos.
- Desenvolva silver em Python com from pyspark import pipelines as dp; desenvolva gold em SQL.
- Mantenha uma transformacao por tabela em transformations/silver/<tabela>.py ou transformations/gold/<tabela>.sql.
- Como a bronze e sobrescrita a cada ingestao, use materialized views com leitura batch (spark.read.table), nunca streaming tables.
- O pipeline e serverless, usa projetoecommerce e tem schema padrao silver. Publique tabelas gold em gold.<tabela>.
- Inicie cada transformacao com comentarios em portugues explicando o motivo das regras.
- Use DECIMAL(10,2) para valores monetarios.
- Marque problemas conhecidos em colunas e expectations warn; nao descarte vendas. Reserve expect_all_or_fail para invariantes.
- Execute databricks bundle validate --strict antes do deploy.

## Regras para tabelas gold

- Use SQL, um arquivo por tabela em `transformations/gold/`, com `CREATE OR REFRESH MATERIALIZED VIEW gold.<tabela>`.
- Declare todas as colunas no esquema da materialized view com tipo e `COMMENT`; inclua também `COMMENT` na tabela explicando quando usá-la.
- Escreva comentários em português, informando unidade (incluindo R$ para valores monetários), regra de cálculo e avisos que evitem interpretações incorretas pelo Genie.
- Inclua todas as vendas em métricas de receita, inclusive vendas de produtos não cadastrados.
- Considere o período dos dados de 13/12/2025 a 11/01/2026.
- Adicione testes para toda nova gold em `testes/testes_qualidade.py`.

## Números de referência do conjunto de dados

Válidos para o período de 13/12/2025 a 11/01/2026; atualize os testes e esta seção se a origem mudar.

- **Silver / vendas:** 3.020 vendas e receita de R$ 974.077,28; 20 vendas de produto sem cadastro (R$ 4.240,01); 5 vendas antes do cadastro do produto (R$ 325,88).
- **Silver / qualidade:** 55 preços de concorrente suspeitos; 11 nomes de clientes com pronome de tratamento. Clientes por região: Norte 17, Nordeste 12, Centro-Oeste 9, Sudeste 8 e Sul 4.
- **Gold / Customer Success:** 50 clientes; 10 VIP, 25 TOP_TIER e 15 REGULAR; maior cliente Ana Sophia Pereira (MG), com R$ 30.716,63.
- **Gold / Comercial:** receita de R$ 974.077,28 em 3.020 vendas; 2.155 vendas no ecommerce.
- **Gold / Pricing:** 215 produtos com preço de concorrente; 35 MAIS_CARO_QUE_TODOS e 15 com pelo menos um preço suspeito.
