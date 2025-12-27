# AI Council API

A Python FastAPI application that orchestrates a council of 7 AI experts (powered by Google Gemini) to debate and evaluate ideas for a Portugal-based development team.

## Council Members

The council consists of 7 members (6 voters + 1 facilitator):

| Role | Focus Area | Votes |
|------|------------|-------|
| **Technical Architect** | Tech feasibility, stack recommendations | ✓ |
| **Venture Capitalist** | Market fit, 0-10 potential score | ✓ |
| **UX Designer** | User journeys, 3-click core task | ✓ |
| **Security Auditor** | GDPR compliance, data risks, priorities | ✓ |
| **Product Owner** | Target audience, value proposition, unmet need | ✓ |
| **Strategic Contrarian** | Stress-tests ideas, challenges assumptions | ✓ |
| **Council Synthesizer** | Facilitates consensus, guides to decision | — |

### Decision Rules
- Each voting member outputs: **Yay** or **Nay** (no "Pivot" allowed)
- Final verdict: **GO** or **NO-GO** based on majority
- If tied, the Synthesizer facilitates another round with adjusted scope

## Virtual Dev Team

A virtual software development team that builds Proofs of Concept (PoCs) using a **sequential pipeline** architecture. Each step feeds its output to the next, ensuring consistency across the stack.

### Pipeline Architecture

```
User Request
     │
     ▼
┌─────────────────────┐
│  Solutions Architect │ → architecture.md (spec, no code)
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Backend Developer   │ → Implements DB + API → backend_report.md
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Frontend Developer  │ → Builds UI using exact API → frontend_report.md
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  DevOps Engineer     │ → Dockerfiles, docker-compose, run.sh
└─────────────────────┘
     │
     ▼
┌─────────────────────┐
│  Team Lead (Reviewer)│ → Cleanup, verify, final summary
└─────────────────────┘
```

### Pipeline Steps

| Step | Role | Input | Output |
|------|------|-------|--------|
| 1 | **Solutions Architect** | User request | `architecture.md` with tech stack, DB schema, API spec, UI design |
| 2 | **Backend Developer** | Architect's spec | Database + API implementation, `backend_report.md` |
| 3 | **Frontend Developer** | Architect's spec + Backend report | UI implementation, `frontend_report.md` |
| 4 | **DevOps Engineer** | All prior context | Dockerfiles, docker-compose.yml, run.sh, README |
| 5 | **Team Lead** | Full project | Cleanup, verification, final summary |

### Key Features
- **Tech Agnostic**: The Architect chooses the best stack for each project.
- **Context Chaining**: Each step receives accumulated output from prior steps.
- **Contract-Based**: Reports act as contracts between pipeline steps.
- **No Hallucination**: Frontend uses exact API endpoints from Backend report.

**Note:** The team works in the `/app/workspace` directory inside the container. To persist their work, mount a volume to this path.

## Prerequisites

- Docker and Docker Compose
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd agno-council

# Create environment file
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or use your preferred editor
```

### 2. Run with Docker Compose

```bash
# Build and start the service
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

The API will be available at `http://localhost:8000`.

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Run a council debate
curl -X POST http://localhost:8000/council/call_council \
  -H "Content-Type: application/json" \
  -d '{"content": "I want to build an AI-powered personal finance app that automatically categorizes expenses and suggests savings opportunities based on spending patterns."}'

# Build a PoC with the Dev Team
curl -X POST http://localhost:8000/dev_team/build_poc \
  -H "Content-Type: application/json" \
  -d '{"content": "Create a simple Python script named hello.py that prints Hello World, and a README.md explaining how to run it."}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info and status |
| `GET` | `/health` | Health check |
| `POST` | `/council/call_council` | Run a council debate |
| `POST` | `/dev_team/build_poc` | Build a Proof of Concept |

### Request Format

```json
{
  "content": "Your idea or note to be debated by the council"
}
```

### Response Format

```json
{
  "status": "success",
  "conclusion": "The council's debate conclusion with Final Verdict..."
}
```

## Local Development

### Without Docker

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=your-api-key
export COUNCIL_GEMINI_MODEL=gemini-2.0-flash-exp
export DEV_TEAM_GEMINI_MODEL=gemini-2.0-flash-exp

# Run the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### With Docker

```bash
# Build the image
docker compose build

# Start the service
docker compose up

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

## Configuration

Environment variables can be set in `.env` file or passed directly:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Your Google Gemini API key |
| `COUNCIL_GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model to use for the council |
| `DEV_TEAM_GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model to use for the dev team |
| `DEBUG` | No | `false` | Enable debug logging |

## Project Structure

```
agno-council/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py      # Application settings
│   ├── council/
│   │   ├── __init__.py
│   │   └── agents.py        # Council agent definitions
│   ├── dev_team/
│   │   ├── __init__.py
│   │   └── agents.py        # Dev Team agent definitions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── council.py       # Council API routes
│   │   └── dev_team.py      # Dev Team API routes
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

## API Documentation

Once running, interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

MIT
