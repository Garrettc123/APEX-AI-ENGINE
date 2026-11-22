# ⚡ APEX — Autonomous Profit & Enterprise eXecution Engine

> **Garcar Enterprise | Built by Garrett Carrol**  
> Experimental multi-agent research and workflow prototype. It is not independently certified for unattended commercial execution, real-estate brokerage, production payments, or revenue.

---

## 🧠 What Is APEX?

APEX is an **unprecedented neuro-symbolic multi-agent AI system** that fuses:

- **LLM Reasoning Agents** (OpenAI GPT-4o / local Ollama fallback)
- **Autonomous Web Intelligence** (scraping, crawling, market scanning)
- **Real Estate Research Pipeline** (locally verified public listing feed; no mocked properties)
- **Stripe Integration Scaffolding** (payments disabled in the autonomous worker pending separate authorization and settlement verification)
- **Swarm Task Orchestration** (parallel agent workers via Celery + Redis)
- **Live Dashboard** (FastAPI + WebSocket real-time UI)
- **Webhook Event Bus** (GitHub, Stripe, Linear, Notion)
- **Self-Healing Retry Logic** (circuit breakers, exponential backoff)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        APEX CORE ENGINE                         │
├───────────┬──────────────┬───────────────┬──────────────────────┤
│  SCOUT    │  ANALYST     │  EXECUTOR     │  MONETIZER           │
│  Agent    │  Agent       │  Agent        │  Agent               │
│           │              │               │                      │
│ Discovery │ Qualification│ Outreach &    │ Stripe invoicing     │
│ Scraping  │ Scoring      │ Deal closing  │ Subscription mgmt    │
│ Market    │ AI reasoning │ CRM updates   │ Revenue reporting    │
│ scanning  │ Risk assess  │ Task routing  │ Payout automation    │
└───────────┴──────────────┴───────────────┴──────────────────────┘
         ↕ Redis Pub/Sub Event Bus ↕
┌─────────────────────────────────────────────────────────────────┐
│              APEX ORCHESTRATOR (FastAPI + Celery)               │
│  - Agent lifecycle management                                   │
│  - Task queue & priority scheduling                             │
│  - WebSocket live dashboard                                     │
│  - REST API (fully documented /docs)                            │
└─────────────────────────────────────────────────────────────────┘
         ↕ Supabase PostgreSQL + Realtime ↕
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT (Railway)                          │
│  - Docker Compose (db + redis + api + 4 role workers)           │
│  - GitHub Actions CI/CD                                         │
│  - Auto-scaling worker pool                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Build & Run

Aligned to the Garcar APEX stack build guide (7 Compose services: `db`, `redis`, `api`, `worker-scout`, `worker-analyst`, `worker-executor`, `worker-monetizer`).

```bash
git clone https://github.com/Garrettc123/APEX-AI-ENGINE
cd APEX-AI-ENGINE
cp .env.example .env
# Fill in your keys in .env (placeholders only in the example)

docker compose up --build
```

Verify:

```bash
curl http://localhost:8000/health
```

- API docs: http://localhost:8000/docs  
- Dashboard: http://localhost:8000  
- ReDoc: http://localhost:8000/redoc  

Workers start via real modules: `python -m apex.workers.{scout,analyst,executor,monetizer}` (Celery consumers on role queues).

> **CASH_LOCK:** do not deploy this stack to Railway from an unapproved PR. Local compose only until cash unlock.

---

## 💰 Revenue Streams Built-In

| Stream | Mechanism | Automated? |
|--------|-----------|------------|
| SaaS Subscriptions | Stripe Billing concept; execution requires a separate approved integration | No |
| Lead Generation Sales | Research-only candidate queue; outbound requires approval | No |
| Real Estate Deal Pipeline | Verified public property research → buy-box screening → operator review | Research only |
| API Access Licensing | Prototype service interfaces; production billing not verified | Unverified |
| White-label Resale | Proposed custom deployment scope | Unverified |

---


## Source-backed Cleburne property research (November 22, 2026)

The prior Scout created dummy properties, fictitious public records and synthetic market signals. The prior Analyst assigned random scores and dollar values; the prior Monetizer counted unsent/unpaid invoices as revenue. **Those behaviors are removed on this branch.**

- Research file: [data/johnson_county_verified_properties.json](data/johnson_county_verified_properties.json)
- Buyer-property matching notes: [docs/johnson_county_property_match_2026-11-22.md](docs/johnson_county_property_match_2026-11-22.md)
- Evidence loader: `apex/agents/property_feed.py` (rejects stale listings after seven days)
- Read-only export: `python -m scripts.property_research_report --json`
- Tests: `python -m unittest discover -s tests -p 'test_verified_property_feed.py'` plus `pytest -q tests/test_health.py`
- Nothing is sent to property owners, investors, CRMs or Stripe. No seller has authorized a transaction; no investor has accepted a deal; no deal profit is established.
- Buyer fit is an *initial published-criteria match*, not proof of funds or a final offer.

### Release gate

This repository branch is draft-only and not deployed. A distinct, audited approval-bound module is required before any outreach, contract, listing marketing, invoice, or deployment. Source refresh is manual until a legitimate property-feed adapter and its permissions are reviewed.

## 📦 Stack

- **Backend:** Python 3.11 + FastAPI
- **Workers:** Celery 5 + Redis
- **Database:** Postgres 16 (Compose) / Supabase (cloud)
- **Payments:** Stripe SDK
- **AI:** OpenAI GPT-4o + LangChain
- **Deploy:** Railway + Docker
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + custom WebSocket dashboard

---

## 📜 License

Proprietary — Garcar Enterprise © 2026. All rights reserved.  
Contact: [github.com/Garrettc123](https://github.com/Garrettc123)


## Nested Docker / local agent hosts

If containers cannot TCP to `db:5432` (common on nested Docker), set in `.env`:

```bash
DATABASE_URL=sqlite+aiosqlite:///./apex.db
```

API startup is soft-fail on DB init so `/health` still comes up. Prefer Postgres when bridge networking works.

