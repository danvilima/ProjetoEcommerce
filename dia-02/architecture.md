# Arquitetura

## Visão geral

```
┌─────────────────────┐      ┌──────────────┐      ┌─────────────────────┐      ┌──────────────────┐
│   Supabase Storage   │      │    boto3     │      │   Spark DataFrame    │      │   Delta Table     │
│  (S3-compatible)     │ ───► │   + pandas   │ ───► │   (Databricks)       │ ───► │  catalogo.bronze  │
│  clientes.parquet    │      │  extract.py  │      │   load.py            │      │  .clientes        │
└─────────────────────┘      └──────────────┘      └─────────────────────┘      └──────────────────┘
```

## Componentes

- **Supabase Storage**: origem dos dados brutos, exportados em formato parquet e
  acessados via protocolo S3 (endpoint compatível exposto pelo Supabase).
- **`src/extract.py`**: client boto3 configurado para o endpoint do Supabase,
  responsável por buscar os arquivos e carregá-los em memória como DataFrames
  pandas (sem passar por disco).
- **`src/load.py`**: converte o DataFrame pandas para Spark e persiste como
  tabela Delta na camada Bronze do Unity Catalog.
- **`notebooks/etl_pipeline.py`**: orquestra a extração e carga de múltiplas
  tabelas, pensado para rodar como notebook/Job no Databricks.

## Por que boto3 + Supabase S3, e não conexão direta ao Postgres?

Os dados já são exportados como parquet para o Storage do Supabase (por outro
processo/rotina), então o pipeline consome diretamente esses arquivos via
protocolo S3 -- mais simples e desacoplado do banco transacional.

## Limitação conhecida: Databricks Free Edition

O Databricks Free Edition disponibiliza apenas compute **serverless**, cujo
egress de rede é restrito por padrão e não permite acesso a domínios externos
como o do Supabase Storage. Esse pipeline requer, portanto, um workspace com:

- Cluster clássico (All-Purpose Compute) com acesso à internet liberado, **ou**
- Network Policy configurada para liberar o domínio do Supabase (disponível
  em tiers Premium/Enterprise).

## Segurança

- Credenciais nunca ficam hardcoded no código; são carregadas via variáveis
  de ambiente (`.env` local) ou, em produção, via **Databricks Secrets**.
- O arquivo `.env` está no `.gitignore` e nunca deve ser commitado.
