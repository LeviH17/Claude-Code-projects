#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# ── Check for API key ──────────────────────────────────────────────────────────
if [ ! -f "$ROOT/backend/.env" ]; then
  echo ""
  echo "  No .env file found. Create one first:"
  echo ""
  echo '  echo "ANTHROPIC_API_KEY=sk-ant-..." > backend/.env'
  echo ""
  exit 1
fi

# ── Install dependencies (skips if already installed) ─────────────────────────
echo "→ Checking backend dependencies..."
pip install -r "$ROOT/backend/requirements.txt" -q

echo "→ Building frontend..."
cd "$ROOT/frontend"
npm install --silent
npm run build

# ── Start the server ──────────────────────────────────────────────────────────
echo ""
echo "  ✓ Ready. Open http://localhost:8000"
echo ""
cd "$ROOT/backend"
uvicorn main:app --port 8000
