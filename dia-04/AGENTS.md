# Dashboards e Genie AI/BI

- Este bundle contem os dashboards executivos e o espaco Genie. As tabelas gold sao produzidas pelo bundle de `dia-03`.
- Use perfil `danvilima`, catalogo `projetoecommerce`, schema `gold` e warehouse `Serverless Starter Warehouse`. O warehouse ID vem do lookup em `databricks.yml`.
- O bundle Genie usa `engine: direct`; seu JSON fonte e `src/genie/diretoria_ecommerce.geniespace.json` e o recurso e `resources/diretoria.genie_space.yml`.
- Identificadores das tabelas Genie permanecem totalmente qualificados como `projetoecommerce.gold.<tabela>` dentro do JSON; DAB nao aplica variaveis de catalogo ao serialized space.
- Edite o JSON versionado e faca deploy para alterar o espaco; nao edite pela interface. O botao Ask Genie dos tres dashboards aponta pelo ID fixo em `uiSettings.genieSpace.overrideId`; o ID de producao sera diferente e deve ser atualizado no JSON antes do deploy de prod.
- Fonte limitada as golds: `vendas_temporais`, `vendas_produtos`, `vendas_detalhadas`, `clientes_segmentacao` e `precos_competitividade`. Nao conectar bronze ou silver. Leia comentarios de tabela/coluna antes de alterar contexto e nao os duplique em instrucoes.
- SQL de exemplos, snippets, relacoes e benchmarks deve usar colunas qualificadas pelo alias/tabela e ser executado com leitura somente antes do deploy. Metricas: periodo fixo 13/12/2025 a 11/01/2026; moeda BRL; nao usar `current_date()`; nao somar `clientes_unicos`; contar produto por `id_produto`; separar suspeitos de confirmados em Pricing.
- Perguntas de producao sao avaliadas via Genie Conversation API contra consultas SQL diretas; guardar cada rodada, pontuacao e mudanca em `docs/validacao-genie.md`. Rode `databricks bundle validate --strict` antes de deploy.
- Genie permissions: `CAN_RUN` para o grupo `diretoria-ecommerce`, criado fora do bundle; atualmente Daniel e membro, pois os outros dois e-mails aprovados ainda nao correspondem a contas encontradas no workspace. Adicione os outros membros quando as contas forem provisionadas.

## Justificativa para instrucoes textuais no Genie

- Texto exato: respostas em portugues; datas relativas sem suporte nao geram SQL; nao estimar lucro/margem; em respostas de Pricing separar confirmados e suspeitos; resumir valores em R$ e citar periodo.
- Por que superficies estruturadas nao bastam: comentarios, sinonimos, relacoes, snippets e SQLs exemplares orientam consulta e calculo, mas nao controlam com consistencia recusas a perguntas sobre datas fora do periodo nem como sintetizar alertas e unidades na resposta conversacional.
- Risco de excesso: instrucoes podem restringir perguntas validas ou conflitar com respostas por dimensao; manter abaixo de 2.000 caracteres e limitadas as regras globais acima.
- Revisao: testar as 10 perguntas de negocio e as duas recusas, comparar com SQL direto e registrar placar e alteracoes em `docs/validacao-genie.md`.
