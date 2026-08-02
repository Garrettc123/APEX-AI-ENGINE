"""APEX Configuration — Pydantic Settings"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    APP_ENV: str = "production"
    APP_SECRET_KEY: str = "change-me"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_FALLBACK_MODEL: str = "gpt-3.5-turbo"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    DATABASE_URL: str = "postgresql://apex:apexpassword@localhost:5432/apex"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_STARTER: str = ""
    STRIPE_PRICE_ID_PRO: str = ""
    STRIPE_PRICE_ID_ENTERPRISE: str = ""

    # MARS API
    MARS_API_KEY: str = ""
    MARS_API_URL: str = "https://api.marsrealty.io/v1"

    # Webhooks
    WEBHOOK_SECRET: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""

    # Notion
    NOTION_TOKEN: str = ""
    NOTION_DATABASE_ID: str = ""

    # Agent Config
    SCOUT_AGENT_CONCURRENCY: int = 5
    ANALYST_AGENT_CONCURRENCY: int = 3
    EXECUTOR_AGENT_CONCURRENCY: int = 2
    MONETIZER_AGENT_CONCURRENCY: int = 2
    AGENT_MAX_RETRIES: int = 3
    AGENT_RETRY_BACKOFF: int = 2

    # Security
    JWT_SECRET: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Sentry
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
