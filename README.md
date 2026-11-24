# Emirates Baggage360

Intelligent baggage orchestration platform for Emirates baggage operations and customer experience stakeholders anchored on Dubai International Airport (DXB).

## Overview

Baggage360 turns distributed baggage and journey signals into a trusted operational picture, identifies baggage exceptions early, coordinates human-led recovery across accountable parties, and keeps passengers informed with accurate, explainable updates.

## Features

- **Consolidated Baggage Journey Visibility** - Track baggage lifecycle milestones (acceptance, transfer, load, arrival, delivery, handover)
- **Journey Context Correlation** - Associate bags with passenger journeys, onward flights, connection windows, and operational changes
- **Source Freshness & Provenance** - Label event sources, timestamps, and staleness indicators
- **Connection Risk Assessment** - Evaluate risk labels, observed vs predicted state, urgency ranking
- **Exception Grouping & Triage** - Group related bags into cases, calculate severity, set deadlines
- **Explainable Recovery Recommendations** - Present recommendations with reason, confidence, freshness, evidence
- **Human Approval Workflow** - Require approval before intervention dispatch
- **Operational Task Dispatch** - Create actionable tasks with bag reference, deadline, context, instructions
- **Partner Role-Scoped Work Queue** - Provide least-privilege task views for partners
- **Task Acknowledgement & Evidence Capture** - Support completion evidence, scan confirmation, handover proof
- **Passenger Baggage Status View** - Display confirmed milestones in plain language
- **Confirmed vs Estimated Separation** - Label uncertainty, avoid unconfirmed guarantees
- **Delayed-Bag Case Status** - Provide next steps for delayed baggage
- **Case Audit Trail** - Track all case activities
- **Executive Reliability & Impact Overview** - Provide aggregated operational intelligence
- **Role-Based Access Control** - Apply differentiated access for operations, partner, passenger, executive roles

## Prerequisites

- **Python 3.11+** - [Download from python.org](https://python.org)
- **Node.js 20.19+ or 22.12+** - [Download from nodejs.org](https://nodejs.org)
- **npm** (included with Node.js)

## Quick Start

### Local Development (SQLite)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd emirates_baggage360
   ```

2. **Start the application**
   ```bash
   # macOS / Linux
   bash start.sh

   # Windows
   start.bat
   ```

   This will:
   - Check prerequisites
   - Create Python virtual environment
   - Install backend dependencies
   - Run database migrations
   - Seed demo data
   - Install frontend dependencies
   - Start backend on http://localhost:9000
   - Start frontend on http://localhost:5173

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:9000
   - API Documentation: http://localhost:9000/docs

4. **Stop the application**
   ```bash
   # macOS / Linux
   bash stop.sh

   # Windows
   stop.bat
   ```

### Demo Credentials

The application is seeded with the following demo users:

| Role | Email | Password |
|------|-------|----------|
| Operations | mariam.alsuwaidi@baggage360.demo | Demo1234! |
| Partner | ahmed.hassan@dnata.ae | Demo1234! |
| Passenger | sara.johnson@example.com | Demo1234! |
| Executive | fatima.albanna@emirates.ae | Demo1234! |

## Docker Deployment

### SQLite (Development)

```bash
# Build and start services
docker compose build
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

Services:
- Frontend: http://localhost:80
- Backend: http://localhost:9000

### PostgreSQL (Production-like)

```bash
# Build and start with PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.postgres.yml build
docker compose -f docker-compose.yml -f docker-compose.postgres.yml up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

Services:
- Frontend: http://localhost:80
- Backend: http://localhost:9000
- PostgreSQL: localhost:5432

## Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install .

# Install dev dependencies
pip install ".[dev]"

# Run migrations
alembic upgrade head

# Seed database
python -m app.seed

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy app --ignore-missing-imports

# Start development server
uvicorn app.main:app --reload --port 9000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Type check
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing

### Backend Tests

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pytest -v --cov=app --cov-report=term-missing
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Tests

```bash
cd frontend
npx playwright test
```

## Configuration

### Backend Configuration

The backend reads configuration from environment variables or `.env` file.

Create `backend/.env` (or copy from `backend/dev.env`):

```env
DATABASE_URL=sqlite:///./app.db
JWT_SECRET_KEY=baggage360-local-dev-secret-change-in-production
CORS_ORIGINS=http://localhost:5173
DEBUG=true
RATE_LIMIT_ENABLED=true
```

### Frontend Configuration

The frontend uses Vite and reads from `import.meta.env`.

No `.env` file is required for local development. The frontend automatically proxies `/api` requests to the backend via Vite's dev server.

For production builds, the nginx configuration in the Docker image handles `/api` proxying.

## Project Structure

```
emirates_baggage360/
├── backend/                 # Python + FastAPI backend
│   ├── app/
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic services
│   │   ├── repositories/   # Data access layer
│   │   ├── middleware/     # Custom middleware
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # Database setup
│   │   ├── main.py         # FastAPI application
│   │   └── seed.py         # Seed data script
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Backend container image
│   ├── docker-entrypoint.sh # Backend entrypoint
│   ├── pyproject.toml      # Python dependencies
│   └── dev.env             # Development environment template
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API client services
│   │   ├── types/          # TypeScript type definitions
│   │   ├── utils/          # Utility functions
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Application entry point
│   ├── e2e/                # End-to-end tests
│   ├── Dockerfile          # Frontend container image
│   ├── nginx.conf.template # Nginx configuration for production
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── docker-compose.yml      # SQLite compose file
├── docker-compose.postgres.yml # PostgreSQL override
├── shared_config.json      # Shared configuration
├── start.sh                # Cross-platform startup script
├── stop.sh                 # Graceful shutdown script
├── start.bat               # Windows wrapper
├── stop.bat                # Windows wrapper
└── README.md               # This file
```

## Architecture

### Backend

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Authentication**: JWT (PyJWT)
- **Database**: SQLite (development), PostgreSQL (production)

### Frontend

- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router
- **Styling**: Tailwind CSS
- **Testing**: Vitest, Playwright

### Database Schema

Key entities:
- **users** - User accounts with role-based access
- **passenger_journeys** - Passenger itineraries
- **journey_legs** - Individual flight segments
- **bags** - Baggage items
- **bag_events** - Immutable baggage scan events
- **exception_cases** - Grouped baggage exceptions
- **case_bags** - Bag-to-case relationships
- **recommendations** - Recovery recommendations
- **approval_decisions** - Human approval records
- **tasks** - Operational tasks
- **task_evidence** - Task completion evidence
- **passenger_case_views** - Passenger-safe projections
- **executive_daily_metrics** - Aggregated metrics
- **audit_events** - Audit trail
- **session_access_log** - Access logs

## API Documentation

Once the backend is running, visit:
- **OpenAPI Docs**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

**Backend Job:**
- Installs Python dependencies
- Runs linter (ruff)
- Runs type checker (mypy)
- Runs tests with PostgreSQL service container
- Generates test coverage report

**Frontend Job:**
- Installs Node dependencies
- Runs linter (eslint)
- Runs type checker (tsc)
- Runs unit tests
- Builds production bundle

## License

Proprietary - Emirates Airlines

## Support

For issues or questions, contact the development team.
