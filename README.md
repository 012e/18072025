# Web Scraper Application

## Requirements

### For Local Development
- Python 3.12 or higher

### For Docker Deployment
- Docker
- Docker Compose (optional)

## Installation

### Option 1: Local Development with uv

#### Installing uv

uv is a fast Python package manager and project manager written in Rust. Choose one of the following installation methods:

**Standalone Installer (Recommended)**
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using wget
wget -qO- https://astral.sh/uv/install.sh | sh
```

**Package Managers**
```bash
# Using pip
pip install uv

# Using pipx (recommended for isolated installation)
pipx install uv

# Using Homebrew (macOS)
brew install uv

# Using Cargo
cargo install --git https://github.com/astral-sh/uv uv
```

#### Project Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd 18072025
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   ```bash
   cp sample.env .env
   ```
   
   Edit `.env` with your actual configuration values:
   ```bash
   GRAFANA_LOKI_URL="https://user:password@your-loki-host/loki/api/v1/push"
   OPENAI_API_KEY="your-openai-api-key"
   REDIS_HOST="your-redis-host"
   REDIS_PORT="6379"
   REDIS_PASSWORD="your-redis-password"
   SCRAPE_OUTPUT_PATH="./.tmp"  # Optional, defaults to ./.tmp
   ```

### Option 2: Docker Deployment

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd 18072025
   ```

2. Set up environment variables:
   ```bash
   cp sample.env .env
   ```
   
   Edit `.env` with your actual configuration values.

3. Build and run with Docker:
   ```bash
   docker build -t scraper-app .
   docker run --env-file .env scraper-app
   ```

## Running the Application

### Local Development

**Using uv (Recommended)**
```bash
uv run main.py
```

**Using Make**
```bash
make run
```

**Manual execution**
```bash
uv run --env-file=.env main.py
```

### Docker

**Direct Docker run**
```bash
docker run --env-file .env scraper-app
```

**With volume mounting for persistent data**
```bash
docker run --env-file .env -v $(pwd)/.tmp:/app/.tmp scraper-app
```

## Testing

Run the test suite:

```bash
# Using uv
uv run pytest

# Using Make
make test
```

## Configuration

The application uses environment variables for configuration. All required variables are listed in `sample.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `GRAFANA_LOKI_URL` | Grafana Loki endpoint for log aggregation | Yes |
| `OPENAI_API_KEY` | OpenAI API key for file processing | Yes |
| `REDIS_HOST` | Redis server hostname | Yes |
| `REDIS_PORT` | Redis server port | Yes |
| `REDIS_PASSWORD` | Redis authentication password | Yes |
| `SCRAPE_OUTPUT_PATH` | Local directory for scraped content | No (defaults to `./.tmp`) |

## Architecture

The application follows a modular architecture:

- **Orchestrator**: Manages the synchronization lifecycle and coordinates between components
- **Scraper**: Handles content extraction from OptiSigns API
- **Diff Checker**: Manages content change detection and versioning
- **Redis Integration**: Provides caching and state management, avoid reuploading the whole collection when re-deploying.
- **Uploader**: Manages file uploads to OpenAI
- **Configuration**: Centralized configuration management with validation

## Development

### Project Structure

```
src/
├── appredis/          # Redis integration
├── config/            # Configuration management
├── diffcheck/         # Content change detection
├── orchestrator/      # Main synchronization logic
├── scraper/           # Web scraping components
├── uploader/          # File upload handling
└── utils/             # Utility functions

tests/                 # Test suite
```

### Code Quality

The project uses pytest for testing. Run tests before committing:

```bash
uv run pytest
```

## Demo

### Sanity test

The support chatbot returned correct data with correct citation for `How do I add a YouTube video?` query.

![Sanity test demo](https://github.com/user-attachments/assets/9c498d6a-09e7-4452-b64a-72ad6bb7f757)

### Logs

You can check out the logs [here](https://huyphmnhat.grafana.net/public-dashboards/f62e8aa337e9402599ee021983b84647?from=now-6h&to=now&timezone=browser)

![Grafana Loki distributed log demo](https://github.com/user-attachments/assets/0026de82-1b90-4027-909b-8e8f1955e853)

## Project reflection

Check that out [here](./Q&A.md).