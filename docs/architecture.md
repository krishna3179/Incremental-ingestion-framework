# Architecture Document

## 1. Architecture Overview

The Incremental Data Ingestion Framework is a Python-based batch ingestion solution. It reads order events from JSON files, validates incoming records, applies incremental processing, and stores the results in a local SQLite database.

The design separates source reading, watermark management, validation, loading, quarantine handling, and pipeline orchestration.

## 2. End-to-End Data Flow

1. Read source events from a JSON file.
2. Retrieve the previously committed watermark for the source.
3. Calculate the extraction start time using the configured lookback window.
4. Select records within the extraction window.
5. Validate required fields, data types, business rules, and customer references.
6. Separate valid records from rejected records.
7. Load valid events into the target database.
8. Maintain event history and processed-event tracking.
9. Store rejected records in quarantine.
10. Calculate and update the watermark.
11. Commit the transaction and record pipeline metrics.

## 3. Incremental Extraction and Watermark

The pipeline uses the source_updated_at field to determine event ordering.

The last successful watermark is stored in the pipeline_watermarks table.

A configurable lookback period is subtracted from the previous watermark to determine the extraction start time.

The default lookback period is 1,440 minutes (24 hours).

This overlap helps capture late-arriving events that have timestamps older than the latest processed event.

The next watermark is calculated using the maximum valid source timestamp selected during the run. The watermark is committed only when the pipeline transaction succeeds.

## 4. Data Validation

The validation layer checks:

- Required fields are present.
- Event IDs are non-empty strings.
- Order and customer IDs are integers.
- Order IDs are positive.
- Customer references exist in the configured valid customer set.
- Amounts are numeric and non-negative.
- Status values are non-empty strings.
- Operations are INSERT, UPDATE, or DELETE.
- Source timestamps are valid ISO-8601 timestamps with timezone information.
- Duplicate event IDs within the input batch are rejected.

Invalid records are separated from valid records and written to quarantine with their validation reasons.

## 5. Target Data Model

### orders

Stores the latest accepted state of each order.

The order_id field is the primary key.

Deletes are represented as soft deletes using the is_deleted flag. This preserves the order record for audit and historical purposes.

### order_history

Stores processed event history, including the event ID, order ID, source timestamp, operation, and source file.

The event_id field prevents duplicate event-history insertion.

### processed_events

Maintains event IDs that have already been processed.

This table supports event-level idempotency during reruns.

### pipeline_watermarks

Stores the last successful watermark for each source.

### pipeline_runs

Stores pipeline execution information, including run ID, start and end times, status, record counts, and error messages.

### quarantine_records

Stores rejected source records, their source file, run ID, and validation reasons.

## 6. Idempotency and Event Ordering

The framework uses event IDs as deterministic processing keys.

Before applying an event, the loader checks whether its event ID already exists in processed_events.

Previously processed events are skipped.

For a new event, the loader records the event in order_history and applies the change to the current orders table.

The current order state is updated only when the incoming source timestamp is newer than the timestamp already stored for that order.

Older events are retained in event history but cannot overwrite a newer current state.

## 7. Delete Handling

DELETE operations use soft deletion.

The corresponding order remains in the orders table, but its is_deleted flag is set.

This approach preserves the record for audit and reconciliation rather than physically removing it.

## 8. Failure Handling and Recovery

The pipeline uses a SQLite transaction for target changes, event tracking, quarantine insertion, and watermark updates.

If an exception occurs during processing:

- The active transaction is rolled back.
- Target changes from that transaction are not committed.
- The watermark remains unchanged.
- The pipeline run is updated with FAILED status and the error message.

A subsequent execution can retry the source data.

The project includes a simulated failure option to verify rollback behavior.

## 9. Observability

Each execution receives a unique run ID.

The pipeline records:

- Start and end timestamps.
- Execution status.
- Input record count.
- Processed record count.
- Rejected record count.
- Error messages for failed executions.

Application logs are written to the reports directory and displayed in the terminal.

## 10. Current Design Limitations

- JSON files are the implemented source format.
- SQLite is used as a local target for demonstration.
- Customer reference validation uses a configured customer ID set.
- The lookback period is time-based and does not replace a dedicated quarantine replay mechanism.
- Large-scale distributed processing and production orchestration are outside the current implementation.

## 11. Potential Production Enhancements

- Add CSV, database, and API source connectors.
- Use configurable schemas and external reference datasets.
- Add quarantine correction and replay workflows.
- Add large-volume performance benchmarks.
- Introduce cloud storage and distributed processing.
- Add centralized monitoring, alerting, and orchestration.
