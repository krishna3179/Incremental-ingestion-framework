# Data Dictionary

## 1. Overview

The Incremental Data Ingestion Framework uses SQLite to store current order
records, event history, pipeline execution metadata, watermarks, processed
event identifiers, and rejected source records.

The database contains six application tables.

## 2. Orders

**Purpose:** Stores the latest state of each order. Updates are applied only
when the incoming source timestamp is newer than the stored timestamp.
Deletes are represented using a soft-delete flag.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| order_id | INTEGER | Yes (primary key) | PK | Unique business identifier for an order |
| customer_id | INTEGER | Yes | | Customer reference identifier |
| amount | REAL | Yes | | Order amount |
| status | TEXT | Yes | | Current order status |
| source_updated_at | TEXT | Yes | | Latest source event timestamp in ISO-8601 format |
| is_deleted | INTEGER | No | | Soft-delete indicator: 0 = active, 1 = deleted |
| last_run_id | TEXT | No | | Pipeline run that last changed the order |

**Grain:** One row per order_id.

## 3. Order History

**Purpose:** Maintains the event history received for orders, including
insert, update, and delete operations.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| event_id | TEXT | Yes (primary key) | PK | Unique source event identifier |
| order_id | INTEGER | Yes | | Business identifier of the affected order |
| customer_id | INTEGER | No | | Customer reference identifier |
| amount | REAL | No | | Order amount carried by the event |
| status | TEXT | No | | Order status carried by the event |
| source_updated_at | TEXT | Yes | | Source event timestamp |
| operation | TEXT | Yes | | Event operation: INSERT, UPDATE, or DELETE |
| source_file | TEXT | No | | Source file from which the event was read |

**Grain:** One row per accepted, previously unprocessed event.

## 4. Pipeline Runs

**Purpose:** Tracks each pipeline execution, including its status,
processing counts, timestamps, and error information.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| run_id | TEXT | Yes (primary key) | PK | Unique identifier for a pipeline execution |
| start_time | TEXT | Yes | | Pipeline start timestamp |
| end_time | TEXT | No | | Pipeline completion or failure timestamp |
| status | TEXT | Yes | | Execution status, such as RUNNING, SUCCESS, or FAILED |
| input_count | INTEGER | No | | Number of selected source records |
| output_count | INTEGER | No | | Number of processed events recorded by the pipeline |
| rejected_count | INTEGER | No | | Number of rejected records in the run |
| error_message | TEXT | No | | Error details when execution fails |

**Grain:** One row per pipeline run.

## 5. Pipeline Watermarks

**Purpose:** Stores the latest successfully committed source timestamp
for each source. The pipeline uses this value to calculate its next
incremental extraction window.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| source_name | TEXT | Yes (primary key) | PK | Name of the source being ingested |
| last_watermark | TEXT | No | | Latest committed source timestamp |

**Grain:** One row per source_name.

## 6. Processed Events

**Purpose:** Maintains event identifiers that have already been processed.
The primary key prevents the same event from being applied more than once.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| event_id | TEXT | Yes (primary key) | PK | Unique processed source event identifier |
| processed_at | TEXT | Yes | | Timestamp when the event was processed |

**Grain:** One row per processed event_id.

## 7. Quarantine Records

**Purpose:** Stores rejected source records and their validation failure
reasons for troubleshooting and data quality monitoring.

| Column | SQLite type | Required | Key | Description |
|---|---|---|---|---|
| quarantine_id | INTEGER | Yes (primary key) | PK | Auto-incremented quarantine record identifier |
| run_id | TEXT | Yes | | Pipeline run associated with the rejection |
| source_file | TEXT | No | | Source file containing the rejected record |
| source_record | TEXT | Yes | | Original rejected record serialized as JSON |
| error_reason | TEXT | Yes | | Validation or rejection reason |

**Grain:** One stored quarantine entry per distinct rejected record and error reason, as enforced by the application logic.

## 8. Data Quality and Design Rules

- event_id must be a non-empty string.
- order_id must be a positive integer.
- customer_id must be an integer from the configured valid customer reference set.
- amount must be numeric and cannot be negative.
- status must be a non-empty string.
- source_updated_at must be a valid ISO-8601 timestamp with a timezone.
- operation must be INSERT, UPDATE, or DELETE.
- Duplicate event identifiers are prevented from being processed again.
- Older events must not overwrite newer order state.
- Deletes are represented as soft deletes to preserve order records.
- Rejected records are retained in quarantine with their error reasons.
- Watermark changes are committed with successful pipeline data changes.

## 9. Schema Notes

- SQLite column types and nullability above were inspected from the actual
  local database using PRAGMA table_info.
- Primary keys are identified from the SQLite schema.
- Application validation rules are implemented in the Python code.
- The current schema does not declare foreign-key relationships between
  these six tables.
- Some application rules, such as valid customer references and allowed
  operations, are enforced by Python validation rather than database
  CHECK constraints.
- The database uses ISO-8601 timestamp strings for timestamp fields.

