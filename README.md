# AI Council API

A Python FastAPI application that orchestrates a council of 7 AI experts (powered by Google Gemini) to debate and evaluate ideas for a Portugal-based development team.

## Council Members

The council consists of 7 members (6 voters + 1 facilitator):

| Name | Role | Focus Area | Votes |
|------|------|------------|-------|
| **Carlos Mendes** | Technical Architect | Tech feasibility, stack recommendations | ✓ |
| **Sofia Almeida** | Venture Capitalist | Market fit, 0-10 potential score | ✓ |
| **Inês Ferreira** | UX Designer | User journeys, 3-click core task | ✓ |
| **Miguel Santos** | Security Auditor | GDPR compliance, data risks, priorities | ✓ |
| **Ana Costa** | Product Owner | Target audience, value proposition, unmet need | ✓ |
| **Dr. Raven Cruz** | Strategic Contrarian | Stress-tests ideas, challenges assumptions | ✓ |
| **João Oliveira** | Council Synthesizer | Facilitates consensus, guides to decision | — |

### Decision Rules
- Each voting member outputs: **Yay** or **Nay** (no "Pivot" allowed)
- Final verdict: **GO** or **NO-GO** based on majority
- If tied, the Synthesizer facilitates another round with adjusted scope

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
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info and status |
| `GET` | `/health` | Health check |
| `POST` | `/council/call_council` | Run a council debate |

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
export GEMINI_MODEL=gemini-2.0-flash-exp

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
| `GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model to use |
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
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── council.py       # API routes
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
