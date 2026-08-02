#!/bin/bash
# APEX Setup Script — Garcar Enterprise
set -e

echo "⚡ APEX AI Engine — Setup"
echo "Garcar Enterprise | Garrett Carrol"
echo "================================"

# Check Python
python3 --version || { echo "Python 3.11+ required"; exit 1; }

# Install deps
pip install -r requirements.txt

# Copy env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ .env created — fill in your API keys"
fi

# Install Playwright browsers
playwright install chromium 2>/dev/null || echo "Playwright install skipped"

echo ""
echo "✅ APEX setup complete!"
echo ""
echo "Next steps:"
echo "  1. Fill in .env with your API keys"
echo "  2. docker-compose up --build"
echo "  3. Open http://localhost:8000"
echo "  4. API docs at http://localhost:8000/docs"
