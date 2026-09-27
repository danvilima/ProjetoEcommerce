# Dia 04 - Dashboards e Genie da Diretoria E-commerce

## Objetivo

Este projeto organiza dashboards executivos e um assistente Genie para as areas Comercial, Customer Success e Pricing. O bundle Databricks reune tres dashboards AI/BI e o Genie Space **Diretoria E-commerce**, que consulta as tabelas gold produzidas em `dia-03`.

## O que foi criado

- `src/dashboards/`: definicoes dos dashboards **Diretoria Comercial**, **Diretoria Customer Success** e **Diretoria Pricing**.
- `resources/*.dashboard.yml`: recursos DAB para os tres dashboards.
- `src/genie/diretoria_ecommerce.geniespace.json`: configuracao versionada do Genie, com tabelas, metadados de colunas, sinonimos, instrucoes, relacoes, exemplos SQL, snippets e benchmarks.
- `resources/diretoria.genie_space.yml`: recurso Genie no bundle, com permissao `CAN_RUN` para o grupo `diretoria-ecommerce`.
- `docs/validacao-genie.md`: resultados dos SQLs de referencia, avaliacoes do Genie e estado do grupo de acesso.
- `AGENTS.md`: orientacoes para manter e validar o bundle.

Os tres dashboards apontam para o Genie pelo campo `uiSettings.genieSpace.overrideId`. Em dev, o ID do Genie e `01f1baaacf1a15e8b6500911c2942879`. Outros ambientes podem ter IDs diferentes; atualize o JSON dos dashboards antes de publica-los nesses ambientes.

## Dados e regras analiticas

O Genie consulta somente estas tabelas de `projetoecommerce.gold`:

- `vendas_temporais` - receita e vendas por data, hora e canal.
- `vendas_produtos` - desempenho de produtos.
- `vendas_detalhadas` - vendas com uma linha por venda.
- `clientes_segmentacao` - receita, compras e segmento por cliente.
- `precos_competitividade` - precos de produtos e comparativos com concorrentes.

O periodo coberto pelos dados e **13/12/2025 a 11/01/2026**. O Genie responde em portugues, informa o periodo analisado e formata valores em reais. Nao ha dados de custo, margem ou lucro. Perguntas sobre datas relativas fora do periodo requerem esclarecimento. Para comparacoes por dia da semana, a receita e agregada por data antes do calculo da media diaria. Em Pricing, itens com preco suspeito sao separados dos confirmados e sinalizados para conferencia.

## Publicacao em dev

Requisitos: Databricks CLI autenticado com o perfil `danvilima`, acesso ao workspace definido em `databricks.yml` e permissao para usar o warehouse `Serverless Starter Warehouse`.

Execute no PowerShell, a partir desta pasta:

```powershell
databricks bundle validate --strict -t dev --profile danvilima
databricks bundle deploy -t dev --profile danvilima
```

Para atualizar somente o Genie:

```powershell
databricks bundle deploy -t dev --profile danvilima --select genie_spaces.diretoria_ecommerce
```

Depois de alterar dashboards, publique-os no workspace com o warehouse configurado. Mantenha os arquivos JSON versionados como fonte da verdade; nao altere apenas pela interface do Databricks.

## Validacao executada

- A validacao estrita do bundle passou.
- O Genie foi implantado com `engine: direct` e as cinco tabelas gold.
- A rodada final dos dez benchmarks terminou com **10/10 corretos**, sem itens pendentes de revisao manual.
- As seis perguntas de exemplo foram verificadas pela Conversation API. A consulta de media percentual por categoria, excluindo precos suspeitos, tambem foi executada diretamente no warehouse.
- Foram verificadas duas recusas: lucro sem dados de custos e uma pergunta com periodo relativo fora da janela dos dados. A API pode anexar um `SELECT` literal com a mensagem de recusa; esse SQL nao consulta tabelas.
- Os detalhes, resultados SQL, avaliacoes e IDs das execucoes estao em [`docs/validacao-genie.md`](docs/validacao-genie.md).

## Acesso

O grupo `diretoria-ecommerce` foi criado e recebeu a permissao `CAN_RUN` no Genie. Daniel (`daniel.vlima021@gmail.com`) e atualmente o unico membro. As contas `soccer432013@gmail.com` e `danvilima@outlook.com` nao foram encontradas no workspace e precisam ser provisionadas antes de serem adicionadas ao grupo.

## Arquivos principais

- [Bundle Databricks](databricks.yml)
- [Configuracao serializada do Genie](src/genie/diretoria_ecommerce.geniespace.json)
- [Recurso Genie](resources/diretoria.genie_space.yml)
- [Resultados de validacao](docs/validacao-genie.md)
