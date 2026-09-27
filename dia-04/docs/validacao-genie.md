# Validacao do Genie Diretoria E-commerce

## Ambiente

- Space dev: `01f1baaacf1a15e8b6500911c2942879` ([Diretoria E-commerce](https://dbc-756aca88-459e.cloud.databricks.com/genie/rooms/01f1baaacf1a15e8b6500911c2942879?w=7474653448966055)).
- Perfil `danvilima`; warehouse `Serverless Starter Warehouse` (`e2c7298d3fd772bc`).
- Periodo dos dados: 13/12/2025 a 11/01/2026.
- Bundle validado com `databricks bundle validate --strict -t dev --profile danvilima`.
- Genie implantado em modo `direct`; os tres dashboards foram atualizados com `uiSettings.genieSpace.overrideId` e publicados.

## Avaliacao dos benchmarks

A rodada final da Genie Evaluation API terminou com **10/10 corretos, 10/10 completos e zero revisoes manuais**.

| Rodada | Eval run ID | Corretos | Observacao |
|---|---|---:|---|
| 1 | `01f1baab09011d4c81787d25a744ee03` | 5/10 | Divergencias em canal, regiao, dia da semana e contagem de precos suspeitos; um erro de formato do juiz. |
| 2 | `01f1baabff591b9eaf4d06d81be602cc` | 6/10 | Regras de grano e filtros reforcadas; quatro comparacoes ainda divergiam. |
| 3 | `01f1baacb98e1f28b38d2f6ec6c7e202` | 7/10 | Benchmarks alinhados ao pedido; tres divergencias restantes. |
| Final | `01f1baad6ec71ce0a12d517e97279c5d` | 10/10 | Todas concluidas como corretas; nenhuma revisao manual. |

## Perguntas de exemplo verificadas via Conversation API

| Pergunta / verificacao | Resultado |
|---|---|
| Receita e vendas por canal | E-commerce: 2.155 vendas e R$ 705.486,21; Loja fisica: 865 vendas e R$ 268.591,07; periodo informado e SQL executado com sucesso. |
| Categorias por receita | Moda R$ 248.124,15; Audio R$ 137.061,47; Acessorios R$ 120.909,94. |
| Distribuicao da carteira | TOP_TIER 25 (50%); REGULAR 15 (30%); VIP 10 (20%). |
| Estados com mais clientes e receita | AM: 4 e R$ 79.474,67; TO: 4 e R$ 71.055,63; PA: 4 e R$ 70.003,51; AC e SP tambem listados. |
| Categoria com maior diferenca percentual media, apenas precos confirmados | A primeira formulacao pediu esclarecimento; apos tornar explicitos a media percentual e o filtro por preco confirmado, respondeu diretamente: Beleza 1,24% (12 produtos), Informatica 0,93% (21), Moda 0,70% (23), Cozinha 0,61% (20), Acessorios 0,42% (23). O SQL foi testado diretamente no warehouse. |
| Produtos com preco suspeito | 15 itens em Tenis; listou exemplos e recomendou confirmacao antes de agir. |

## Recusas de seguranca

- `Qual foi o lucro hoje?`: recusou lucro por falta de custo/margem, ofereceu consultar receita; nenhum SQL de dados foi gerado.
- `Quanto vendemos esta semana?`: explicou que a semana nao esta definida dentro do periodo e pediu datas. A API anexou um `SELECT` literal com a mensagem de recusa; ele nao consultou tabelas.

## SQL de referencia

| Pergunta/checagem | Resultado direto validado |
|---|---|
| Receita total | R$ 974.077,28 |
| Categoria lider | Moda; R$ 248.124,15 |
| Cinco produtos lideres | Fone de Ouvido Esportivo R$ 116.462,65; Camisa Social R$ 115.794,92; Necessaire R$ 63.668,43; Persiana Vertical R$ 42.310,56; Calca Jeans Skinny R$ 41.313,34 |
| Clientes VIP | 10; receita R$ 262.806,22; 27,0% da receita |
| Regiao lider | Norte; R$ 333.078,69; 17 clientes |
| Maior media diaria | Quarta-feira; R$ 34.753,61 (4 datas) |
| Mais caro que todos os concorrentes | 15 suspeitos em Tenis e 20 confirmados |
| Diferenca percentual media por categoria sem suspeitos | Beleza +1,24%; Informatica +0,93%; Moda +0,70%; Cozinha +0,61%; Acessorios +0,42% |

## Acesso ao grupo

O grupo `diretoria-ecommerce` foi criado com ID `2120577432192739` e a permissao Genie `CAN_RUN` foi implantada. Daniel (`daniel.vlima021@gmail.com`, user ID `77385503662697`) foi adicionado. As contas `soccer432013@gmail.com` e `danvilima@outlook.com` nao foram encontradas no workspace (busca por `userName` e por e-mail); adiciona-las quando forem provisionadas. Ate la, somente Daniel tem acesso pelo grupo.

## Manutencao

Depois de alterar JSON, execute SQLs afetados no warehouse, valide e implante o recurso Genie. Registre aqui novas avaliacoes, respostas da Conversation API, SQL gerado e alteracoes que levaram a cada correcao.
