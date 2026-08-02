#!/bin/bash
# APEX Test Runner
set -e
echo "⚡ Running APEX Test Suite"
export APP_ENV=testing
export APP_SECRET_KEY=test-secret
export DATABASE_URL=sqlite+aiosqlite:///./test.db
export REDIS_URL=redis://localhost:6379/0
export CELERY_BROKER_URL=redis://localhost:6379/1
export CELERY_RESULT_BACKEND=redis://localhost:6379/2
pytest tests/ -v --tb=short --asyncio-mode=auto
echo "✅ All tests passed"
