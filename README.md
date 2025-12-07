# Time Series Metrics API

A FastAPI-based time series metrics ingestion and query service with automatic rollups and retention policies.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env` file

3. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health
- `GET /health` - Service status
- `GET /db/status` - Database connection status

### Ingestion
- `POST /metrics/ingest` - Ingest a single metric

### Query
- `GET /metrics/names` - Get list of available metric names
- `GET /query/raw` - Fetch raw data without aggregation
- `GET /query/rollup` - Fetch pre-computed rollup data

### Anomaly Detection
- `GET /anomaly/detect` - Detect anomalies using z-score analysis

### Backfill
- `POST /backfill/import` - Import historical data in bulk

### Dashboard
- `GET /` or `GET /dashboard` - Interactive dashboard with:
  - Line chart visualization
  - Metric selector with rollup options (raw/1m/5m/1h)
  - Time range selector (1h/24h/7d)
  - Data table view

Access: http://localhost:8000

## Background Jobs

### Rollup Job
```bash
python -m app.jobs.rollup_job
```

### Retention Job
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

### Query

**Get available metrics:**
```bash
curl "http://localhost:8000/metrics/names"
```

**Query raw data:**
```bash
curl "http://localhost:8000/query/raw?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T23:59:59Z"
```

**Query rollup data:**
```bash
curl "http://localhost:8000/query/rollup?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T12:00:00Z&window=5m"
```


### Anomaly Detection

```bash
curl "http://localhost:8000/anomaly/detect?metric_name=cpu_usage&start_time=2025-12-03T00:00:00Z&end_time=2025-12-03T23:59:59Z&threshold=3.0"
```

### Backfill

```bash
curl -X POST "http://localhost:8000/backfill/import" \
  -H "Content-Type: application/json" \
  -d '{
    "metrics": [
      {
        "metric_name": "cpu_usage",
        "value": 75.5,
        "timestamp": "2025-12-01T12:00:00Z",
        "labels": {"host": "server1"}
      },
      {
        "metric_name": "cpu_usage",
        "value": 76.2,
        "timestamp": "2025-12-01T12:01:00Z",
        "labels": {"host": "server1"}
      }
    ]
  }'
```

## Features

- Real-time metric ingestion
- Automatic rollup generation (1m, 5m, 1h)
- Configurable retention policies
- Label-based filtering
- Anomaly detection using z-score analysis
- Interactive web dashboard
- Bulk historical data import
- Cardinality limit protection

## Architecture

- **FastAPI** - High-performance async API framework
- **PostgreSQL** - Time series data storage with JSONB labels
- **SQLAlchemy** - ORM for database operations
- **Chart.js** - Dashboard visualizations
- **Background Jobs** - Automated rollup and retention management
