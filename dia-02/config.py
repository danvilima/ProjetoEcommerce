"""
Configuração centralizada do projeto.

Carrega variáveis de ambiente de um arquivo .env (uso local) ou do
ambiente já configurado (ex: Databricks Secrets injetados como env vars).

Nunca coloque credenciais reais diretamente neste arquivo.
"""

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_ENDPOINT_URL = os.getenv("SUPABASE_ENDPOINT_URL")
SUPABASE_REGION = os.getenv("SUPABASE_REGION")
SUPABASE_ACCESS_KEY_ID = os.getenv("SUPABASE_ACCESS_KEY_ID")
SUPABASE_SECRET_ACCESS_KEY = os.getenv("SUPABASE_SECRET_ACCESS_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")


def validate_config() -> None:
    """Valida se todas as variáveis obrigatórias foram carregadas."""
    required = {
        "SUPABASE_ENDPOINT_URL": SUPABASE_ENDPOINT_URL,
        "SUPABASE_REGION": SUPABASE_REGION,
        "SUPABASE_ACCESS_KEY_ID": SUPABASE_ACCESS_KEY_ID,
        "SUPABASE_SECRET_ACCESS_KEY": SUPABASE_SECRET_ACCESS_KEY,
        "SUPABASE_BUCKET": SUPABASE_BUCKET,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise EnvironmentError(
            f"Variáveis de ambiente ausentes: {', '.join(missing)}. "
            "Verifique seu arquivo .env ou as Databricks Secrets configuradas."
        )
