# RequirementsSuperTool

An AI-powered requirements generation platform. Users answer domain-specific questions and the system generates structured software requirements (functional, non-functional, use cases, and SRS documents) using Claude AI combined with a domain knowledge base stored in Qdrant.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, SQLAlchemy, PostgreSQL |
| AI | Anthropic Claude API |
| Vector DB | Qdrant Cloud |

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16
- A [Qdrant Cloud](https://cloud.qdrant.io) cluster
- An [Anthropic API key](https://console.anthropic.com)

## Local Development

### 1. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_lg

# Configure environment
copy .env.example .env
# Edit .env with your database URL, API keys, and SMTP credentials

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python -m app.seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# .env.local is already created — edit if your backend runs on a different port
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start the dev server
npm run dev
```

Frontend runs at `http://localhost:3000`

## Docker (All Services)

```bash
# Copy and fill in the backend environment file
copy backend\.env.example backend\.env
# Edit backend/.env with your credentials

# Build and start everything
docker-compose up --build
```

After startup:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

Run database migrations inside Docker:

```bash
docker-compose exec backend alembic upgrade head
```

## Environment Variables

See [backend/.env.example](backend/.env.example) for all required variables and descriptions.

Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (use a long random string) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `QDRANT_URL` | Qdrant cluster URL |
| `QDRANT_API_KEY` | Qdrant API key |
| `SMTP_USER` / `SMTP_PASSWORD` | Gmail SMTP credentials for email |
| `FRONTEND_URL` | Frontend base URL (for email links) |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins |
