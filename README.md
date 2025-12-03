# Time Series Metrics API

A FastAPI-based time series metrics ingestion and query service with automatic rollups and retention policies.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env` file (already configured)

3. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health
- `GET /` - Basic health check
- `GET /health` - Service status
- `GET /db/status` - Database connection status

### Ingestion
- `POST /metrics/ingest` - Ingest a single metric

### Metrics Discovery
- `GET /metrics/list` - List all metrics with pagination
- `GET /metrics/{metric_name}/info` - Get detailed metric information

### Query
- `POST /query` - Query with aggregation (auto-selects optimal source)
- `GET /query/raw` - Fetch raw data without aggregation
- `GET /query/rollup` - Fetch pre-computed rollup data

### Rollups
- `GET /rollups` - List all available rollups

## Background Jobs

### Rollup Job (runs every 60 seconds)
```bash
python -m app.jobs.rollup_job
```

### Retention Job (runs every 24 hours)
```bash
python -m app.jobs.retention_job
```

## Data Generator

Generate test data:
```bash
python -m app.services.data_generator --metric cpu_usage --pattern sine_wave --duration 300 --interval 5 --base-url http://localhost:8000
```

Patterns: noise, sine_wave, linear_trend, spike, combined

## API Examples

### Ingestion

**Ingest a metric:**
```bash
curl -X POST "http://localhost:8000/metrics/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "value": 75.5,
    "timestamp": "2025-12-03T12:00:00Z",
    "labels": {"host": "server1", "region": "us-west"}
  }'
```

### Metrics Discovery

**List all metrics:**
```bash
curl "http://localhost:8000/metrics/list?page=1&page_size=10"
```

**Search metrics:**
```bash
curl "http://localhost:8000/metrics/list?search=cpu"
```

**Get metric details:**
```bash
curl "http://localhost:8000/metrics/cpu_usage/info"
```

### Query

**Query with aggregation (POST):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "metric_name": "cpu_usage",
    "start_time": "2025-12-03T00:00:00Z",
    "end_time": "2025-12-03T23:59:59Z",
    "labels": {"host": "server1"},
    "function": "avg"
  }'
```

Available functions: `avg`, `sum`, `min`, `max`, `count`, `rate`, `raw`

**Query raw data (GET):**
```bash
curl "http://localhost:8000/query/raw?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T23:59:59Z"
```

**Query raw data with labels:**
```bash
curl "http://localhost:8000/query/raw?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T23:59:59Z&labels=%7B%22host%22:%22server1%22%7D"
```

**Query rollup data (GET):**
```bash
curl "http://localhost:8000/query/rollup?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T12:00:00Z&window=5m"
```

Available windows: `1m`, `5m`, `1h`

### Rollups

**List all rollups:**
```bash
curl "http://localhost:8000/rollups"
```

**List rollups for specific metric:**
```bash
curl "http://localhost:8000/rollups?metric_name=cpu_usage"
```
