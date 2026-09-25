"""
Extração de arquivos parquet do Supabase Storage via protocolo S3.

O Supabase Storage expõe um endpoint compatível com S3, permitindo o uso
do boto3 como client. Note que o Supabase permite espaços em nomes de
bucket, algo que o boto3 valida por padrão -- por isso desabilitamos essa
validação específica abaixo.
"""

import io
import logging

import boto3
import botocore.handlers
import pandas as pd
from botocore.client import Config

from src.config import (
    SUPABASE_ACCESS_KEY_ID,
    SUPABASE_BUCKET,
    SUPABASE_ENDPOINT_URL,
    SUPABASE_REGION,
    SUPABASE_SECRET_ACCESS_KEY,
)

logger = logging.getLogger(__name__)


def get_s3_client():
    """Cria e retorna um client boto3 configurado para o Supabase Storage."""
    client = boto3.client(
        "s3",
        endpoint_url=SUPABASE_ENDPOINT_URL,
        aws_access_key_id=SUPABASE_ACCESS_KEY_ID,
        aws_secret_access_key=SUPABASE_SECRET_ACCESS_KEY,
        region_name=SUPABASE_REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )
    # Supabase aceita espaços em nomes de bucket; a validação padrão do
    # boto3 rejeitaria esses nomes antes mesmo da requisição ser feita.
    client.meta.events.unregister(
        "before-parameter-build.s3", botocore.handlers.validate_bucket_name
    )
    return client


def list_available_files(bucket: str = SUPABASE_BUCKET) -> list[str]:
    """Lista as chaves (arquivos) disponíveis em um bucket."""
    s3_client = get_s3_client()
    response = s3_client.list_objects_v2(Bucket=bucket)
    return [obj["Key"] for obj in response.get("Contents", [])]


def extract_parquet(key: str, bucket: str = SUPABASE_BUCKET) -> pd.DataFrame:
    """
    Extrai um arquivo parquet do Supabase Storage e retorna um DataFrame pandas.

    Args:
        key: caminho/nome do arquivo no bucket (ex: "clientes.parquet").
        bucket: nome do bucket de origem.

    Returns:
        DataFrame pandas com o conteúdo do arquivo parquet.
    """
    logger.info("Extraindo '%s' do bucket '%s'", key, bucket)
    s3_client = get_s3_client()
    response = s3_client.get_object(Bucket=bucket, Key=key)
    parquet_bytes = response["Body"].read()
    df = pd.read_parquet(io.BytesIO(parquet_bytes))
    logger.info("'%s' extraído com sucesso: %d linhas, %d colunas", key, *df.shape)
    return df
