# Incremental Data Ingestion Framework

A Python-based incremental data ingestion framework using SQLite as a local target database. It demonstrates watermark-based extraction, data validation, deduplication, upserts, soft deletes, event history, quarantine handling, and safe recovery from failures.

## 1. Project Overview

This project implements a small, reproducible data engineering pipeline that processes order events from JSON files and publishes validated data into SQLite.

The framework focuses on:
- Incremental processing using source timestamps and watermarks.
- Lookback windows to capture late-arriving events.
- Idempotent processing to prevent duplicate event application.
- Insert, update, and delete event handling.
- Protection against stale events overwriting newer records.
- Data validation and quarantine of rejected records.
- Transaction rollback and pipeline failure logging.
- Automated testing with pytest.

## 2. Architecture

```text
JSON Source Files
       |
       v
Source Reader
       |
       v
Incremental Extraction
(Watermark + Lookback)
       |
       v
Data Validation
       |
       +--------------------+
       |                    |
       v                    v
Valid Events          Rejected Events
       |                    |
       v                    v
Transformation         Quarantine
       |
       v
SQLite Loader
       |
       +------------------------------+
       |              |               |
       v              v               v
    Orders       Order History   Processed Events
       |
       v
Pipeline Watermarks
       |
       v
Run Metrics and Logs
```

See [Architecture Documentation](docs/architecture.md) for details.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Pipeline implementation |
| SQLite | Local target database and control tables |
| JSON | Source event format |
| pytest | Automated testing |
| Git | Version control |

## 4. Project Structure

```text
incremental-ingestion-framework/
|
|-- data/
|   |-- input/
|   |-- sample/
|   |-- output/
|
|-- src/
|   |-- config.py
|   |-- database.py
|   |-- source_reader.py
|   |-- watermark.py
|   |-- validator.py
|   |-- transformer.py
|   |-- loader.py
|   |-- quarantine.py
|   |-- logger.py
|   |-- pipeline.py
|
|-- scripts/
|   |-- generate_data.py
|
|-- tests/
|   |-- test_ingestion.py
|   |-- test_idempotency.py
|   |-- test_watermark.py
|   |-- test_deletes.py
|   |-- test_recovery.py
|   |-- test_validation.py
|   |-- test_pipeline.py
|
|-- docs/
|   |-- architecture.md
|   |-- data_dictionary.md
|   |-- design_decisions.md
|
|-- reports/
|   |-- reconciliation.md
|
|-- requirements.txt
|-- pytest.ini
|-- README.md
|-- .gitignore
```

## 5. Setup Instructions

### Prerequisites

- Python 3.12 or compatible version
- Git
- Windows, Linux, or macOS

### Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

## 6. Generate Sample Data

Run:

```powershell
python scripts/generate_data.py
```

The generator creates reproducible sample order events for pipeline execution and testing.

## 7. Run the Pipeline

Run the default sample:

```powershell
python -m src.pipeline
```

To process another JSON source file:

```powershell
python -c "from src.pipeline import run_pipeline; print(run_pipeline(source_file='data/input/late_arriving_event.json', source_name='orders'))"
```

The pipeline reports its run ID, execution status, input and output metrics, rejected records, and processing metrics.

## 8. Run Automated Tests

Run the complete test suite:

```powershell
pytest -v
```

The current test suite contains 18 automated tests, all passing in the local development environment.

Test coverage includes:
- Data validation and required fields.
- Invalid customer references and negative amounts.
- Watermark calculation and lookback.
- Duplicate event handling and idempotency.
- Updates, deletes, and stale-event protection.
- Pipeline rollback after simulated failure.
- Malformed JSON handling.

## 9. Database Tables

| Table | Purpose |
|---|---|
| orders | Current order state |
| order_history | Processed event history |
| processed_events | Event-level idempotency tracking |
| pipeline_watermarks | Last successful source watermark |
| pipeline_runs | Pipeline execution status and metrics |
| quarantine_records | Rejected source records and validation reasons |

See [Data Dictionary](docs/data_dictionary.md) for details.

## 10. Execution Evidence

The local reconciliation report records the development database snapshot and tested scenarios.

See [Reconciliation Report](reports/reconciliation.md).

## 11. Current Implementation Scope

- JSON file ingestion.
- SQLite local target.
- Timestamp-based incremental extraction.
- Configured lookback window.
- Event-level deduplication.
- Insert, update, and soft-delete operations.
- Validation and quarantine.
- Transaction-based recovery.
- Pipeline logging and execution metrics.

## 12. Known Limitations

- The current source reader supports JSON files; additional source formats require implementation.
- SQLite is used for local demonstration, not as a distributed production data platform.
- Customer reference validation currently uses a configured set of valid customer IDs.
- The current performance evidence is functional testing, not a large-scale benchmark.
- Production deployment would require additional security, orchestration, monitoring, and scalability controls.

## 13. Future Enhancements

- CSV and database source connectors.
- Configurable schemas and reference datasets.
- Quarantine replay and correction workflows.
- Large-volume performance benchmarking.
- Cloud deployment using Azure Data Factory, Azure Data Lake Storage, and Databricks.

## 14. Author

Developed as a practical data engineering project demonstrating incremental ingestion, data quality, idempotency, and recovery patterns.
