#!/bin/bash
# start.sh — Start the Emirates Baggage360 application
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Convert path for native Windows programs under Git Bash
native_path() { 
    if command -v cygpath >/dev/null 2>&1; then 
        cygpath -m "$1"
    else 
        printf '%s' "$1"
    fi
}

# Port detection (lsof on macOS/Linux, netstat under Git Bash on Windows)
port_in_use() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -iTCP:"$1" -sTCP:LISTEN -t >/dev/null 2>&1
    else
        netstat -an 2>/dev/null | grep -Eq "[:.]$1[[:space:]].*LISTEN"
    fi
}

find_available_port() {
    local port=$1
    while port_in_use "$port"; do
        echo "Port $port in use, trying $((port+1))..." >&2
        port=$((port+1))
    done
    echo $port
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    # Probe by running it: under Git Bash `python3` may be the Windows Store stub.
    PYTHON=""
    for c in python3 python; do
        if "$c" -c 'import sys' >/dev/null 2>&1; then PYTHON=$c; break; fi
    done
    if [ -n "$PYTHON" ]; then
        PYTHON_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
            echo "❌ Python 3.11+ required (found $PYTHON_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Python $PYTHON_VERSION"
        fi
    else
        echo "❌ Python 3 not found. Install from https://python.org"
        errors=$((errors+1))
    fi

    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        NODE_MINOR=$(echo $NODE_VERSION | cut -d. -f2)
        if [ "$NODE_MAJOR" -lt 20 ] || ([ "$NODE_MAJOR" -eq 20 ] && [ "$NODE_MINOR" -lt 19 ]); then
            if [ "$NODE_MAJOR" -lt 22 ] || ([ "$NODE_MAJOR" -eq 22 ] && [ "$NODE_MINOR" -lt 12 ]); then
                echo "❌ Node.js 20.19+ or 22.12+ required (found $NODE_VERSION)"
                errors=$((errors+1))
            else
                echo "✓ Node.js $NODE_VERSION"
            fi
        else
            echo "✓ Node.js $NODE_VERSION"
        fi
    else
        echo "❌ Node.js not found. Install from https://nodejs.org"
        errors=$((errors+1))
    fi

    if ! command -v npm &>/dev/null; then
        echo "❌ npm not found"
        errors=$((errors+1))
    else
        echo "✓ npm $(npm --version)"
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

check_prerequisites

# === Backend Setup ===
echo "=== Setting up backend ==="
cd backend

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    "$PYTHON" -m venv .venv
fi

# Windows venvs (Git Bash) have Scripts/, macOS/Linux venvs have bin/
if [ -f .venv/Scripts/activate ]; then 
    source .venv/Scripts/activate
else 
    source .venv/bin/activate
fi

echo "Installing backend dependencies..."
pip install . -q

# Copy dev.env to .env if .env doesn't exist
if [ ! -f .env ] && [ -f dev.env ]; then
    echo "Copying dev.env to .env..."
    cp dev.env .env
fi

# Database setup with absolute path
DB_PATH="$SCRIPT_DIR/backend/app.db"
export DATABASE_URL="sqlite:///$(native_path "$DB_PATH")"

echo "Running database migrations..."
python -m alembic upgrade head

echo "Seeding database..."
python -m app.seed

cd "$SCRIPT_DIR"

# === Frontend Setup ===
echo ""
echo "=== Setting up frontend ==="
cd frontend

echo "Installing frontend dependencies..."
npm install -q

cd "$SCRIPT_DIR"

# === Start Services ===
echo ""
echo "=== Starting services ==="

# Find available ports
BACKEND_PORT=$(find_available_port 9000)
FRONTEND_PORT=$(find_available_port 5173)

# Update CORS in backend/.env to include the frontend port
echo "Updating CORS configuration..."
cd backend
if [ -f .env ]; then
    # Portable way to update CORS_ORIGINS line
    if grep -q "^CORS_ORIGINS=" .env; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:${FRONTEND_PORT}|" .env
        else
            sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:${FRONTEND_PORT}|" .env
        fi
    else
        echo "CORS_ORIGINS=http://localhost:${FRONTEND_PORT}" >> .env
    fi
fi
cd "$SCRIPT_DIR"

# Start backend
echo "Starting backend on http://localhost:$BACKEND_PORT"
cd backend
if [ -f .venv/Scripts/activate ]; then 
    source .venv/Scripts/activate
else 
    source .venv/bin/activate
fi
uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!
cd "$SCRIPT_DIR"

# Start frontend with backend port in environment
echo "Starting frontend on http://localhost:$FRONTEND_PORT"
cd frontend
BACKEND_PORT="$BACKEND_PORT" npm run dev -- --port "$FRONTEND_PORT" &
FRONTEND_PID=$!
cd "$SCRIPT_DIR"

# Save PIDs
echo "$BACKEND_PID" > .pids
echo "$FRONTEND_PID" >> .pids

echo ""
echo "=== Emirates Baggage360 is running ==="
echo ""
echo "  Frontend:  http://localhost:$FRONTEND_PORT"
echo "  Backend:   http://localhost:$BACKEND_PORT"
echo "  API Docs:  http://localhost:$BACKEND_PORT/docs"
echo ""
echo "=== Demo Credentials ==="
echo "  Operations: mariam.alsuwaidi@baggage360.demo / Demo1234!"
echo "  Partner:    ahmed.hassan@dnata.ae / Demo1234!"
echo "  Passenger:  sara.johnson@example.com / Demo1234!"
echo "  Executive:  fatima.albanna@emirates.ae / Demo1234!"
echo ""
echo "Press Ctrl+C to stop all services"
wait
