#!/usr/bin/env bash
# BGSTM One-Command Setup Script (Unix/macOS)
set -euo pipefail

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
echo -e "${BLUE}"
echo "  ██████   ██████  ███████ ████████ ███    ███ "
echo "  ██   ██ ██       ██         ██    ████  ████ "
echo "  ██████  ██   ███ ███████    ██    ██ ████ ██ "
echo "  ██   ██ ██    ██      ██    ██    ██  ██  ██ "
echo "  ██████   ██████  ███████    ██    ██      ██ "
echo -e "${NC}"
echo -e "${CYAN}  BGSTM One-Command Installer${NC}"
echo "  ─────────────────────────────────────────────"
echo ""

# ---------------------------------------------------------------------------
# 1. Check requirements: Docker and Docker Compose
# ---------------------------------------------------------------------------
info "Checking requirements..."

if ! command -v docker &>/dev/null; then
    error "Docker is not installed."
    echo ""
    echo "  Please install Docker Desktop (includes Docker Compose):"
    echo "    macOS:  https://docs.docker.com/desktop/install/mac-install/"
    echo "    Linux:  https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

if ! docker info &>/dev/null; then
    error "Docker daemon is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Support both 'docker compose' (v2 plugin) and 'docker-compose' (v1 standalone)
if docker compose version &>/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose &>/dev/null; then
    DC="docker-compose"
else
    error "Docker Compose is not available."
    echo ""
    echo "  Please install Docker Desktop (which includes Docker Compose):"
    echo "    https://docs.docker.com/desktop/install/"
    echo ""
    exit 1
fi

success "Docker $(docker --version | cut -d' ' -f3 | tr -d ',') and Docker Compose found."

# ---------------------------------------------------------------------------
# 2. Copy .env.example → .env (idempotent)
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f ".env" ]; then
    warn ".env already exists — skipping copy (using existing file)."
else
    if [ ! -f ".env.example" ]; then
        error ".env.example not found. Are you running this script from the BGSTM root directory?"
        exit 1
    fi
    cp .env.example .env
    success "Created .env from .env.example."
fi

# ---------------------------------------------------------------------------
# 3. Start all services
# ---------------------------------------------------------------------------
info "Starting services with Docker Compose (this may take a few minutes on first run)..."
$DC up -d --build

success "Docker Compose services started."

# ---------------------------------------------------------------------------
# 4. Health checks
# ---------------------------------------------------------------------------
TIMEOUT=120
INTERVAL=5

wait_for() {
    local name="$1"
    local url="$2"
    local elapsed=0

    info "Waiting for $name to be ready..."
    while true; do
        if curl -sf --max-time 3 "$url" &>/dev/null; then
            success "$name is ready."
            return 0
        fi
        if [ "$elapsed" -ge "$TIMEOUT" ]; then
            error "$name did not become ready within ${TIMEOUT}s."
            echo ""
            echo "  Troubleshooting tips:"
            echo "    • Check logs:   $DC logs -f"
            echo "    • Common cause: port already in use (80 or 8000)"
            echo "    • Try:          $DC down && $DC up -d --build"
            echo ""
            return 1
        fi
        sleep "$INTERVAL"
        elapsed=$((elapsed + INTERVAL))
        echo -ne "    ${YELLOW}...${NC} ${elapsed}s / ${TIMEOUT}s\r"
    done
}

wait_for "Backend API"  "http://localhost:8000/health"
wait_for "Frontend"     "http://localhost"

# ---------------------------------------------------------------------------
# 5. Optional: load sample data
# ---------------------------------------------------------------------------
echo ""
read -r -p "$(echo -e "${CYAN}Load sample data?${NC} (y/n) ")" LOAD_SAMPLE
echo ""
if [[ "${LOAD_SAMPLE,,}" == "y" || "${LOAD_SAMPLE,,}" == "yes" ]]; then
    info "Loading sample data..."
    if $DC exec backend python -m app.db.sample_data; then
        success "Sample data loaded."
    else
        warn "Sample data load encountered an error. You can retry manually:"
        warn "  $DC exec backend python -m app.db.sample_data"
    fi
else
    info "Skipping sample data."
fi

# ---------------------------------------------------------------------------
# 6. Open browser
# ---------------------------------------------------------------------------
info "Attempting to open browser at http://localhost ..."
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost" &>/dev/null &
elif command -v open &>/dev/null; then
    open "http://localhost"
elif command -v sensible-browser &>/dev/null; then
    sensible-browser "http://localhost" &>/dev/null &
else
    warn "Could not detect a browser opener. Please open http://localhost manually."
fi

# ---------------------------------------------------------------------------
# 7. Summary
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅  BGSTM is up and running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${CYAN}Frontend:${NC}    http://localhost"
echo -e "  ${CYAN}Backend API:${NC} http://localhost:8000"
echo -e "  ${CYAN}API Docs:${NC}    http://localhost:8000/docs"
echo ""
echo -e "  ${YELLOW}Stop services:${NC}  $DC down"
echo -e "  ${YELLOW}View logs:${NC}      $DC logs -f"
echo ""
