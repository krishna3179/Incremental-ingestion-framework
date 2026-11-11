# Design Decisions

## 1. Project Scope

This project implements a local batch-based incremental ingestion framework
using Python, JSON source files, and SQLite.

The design prioritizes correctness, repeatable execution, data quality,
idempotency, recovery, and observability over production-scale infrastructure.

## 2. Technology Choices

| Component | Choice | Reason |
|---|---|---|
| Programming language | Python | Readable implementation and test support |
| Source format | JSON | Simple, reproducible event-based input |
| Target database | SQLite | Local execution without external infrastructure |
| Test framework | pytest | Automated functional and edge-case testing |
| Timestamp format | ISO-8601 with timezone | Consistent timestamp interpretation |

## 3. Source and Event Model

The source contains order events with these main attributes:

- event_id: unique identifier for an event.
- order_id: business identifier for an order.
- customer_id: customer reference identifier.
- amount: order amount.
- status: order status.
- source_updated_at: source event timestamp.
- operation: INSERT, UPDATE, or DELETE.

The order_id represents the business key. The event_id identifies an
individual source event.

## 4. Incremental Processing and Watermarks

The pipeline uses source_updated_at to determine the incremental
processing window.

The default lookback period is 1,440 minutes (24 hours).

A lookback window is used to capture late-arriving events and events
received out of chronological order.

The watermark is calculated from the maximum valid timestamp among
selected timestamped records. It is not allowed to move backwards.

The watermark update is committed in the same database transaction as
the corresponding target changes.

## 5. Idempotency and Duplicate Handling

The processed_events table stores event identifiers that have already
been processed.

The event_id primary key prevents an event from being applied more than
once.

The orders table uses order_id as its primary key and applies changes
through an upsert operation.

Repeated input events therefore do not create duplicate order records
or duplicate event-history entries.

## 6. Event Ordering and Stale Updates

Events are processed in source timestamp order.

An incoming event updates the current order state only when its
source_updated_at is newer than the timestamp already stored.

Older events are treated as stale and do not overwrite newer order state.

The event history and processing metrics provide visibility into
previously unseen events, including stale events.

## 7. Delete Handling

Deletes are implemented as soft deletes.

The orders table retains the order record and sets is_deleted to 1.

This preserves the current record for audit and reconciliation purposes
instead of physically removing it.

## 8. Data Quality and Quarantine

Validation is performed before valid events are loaded.

The validation rules cover required fields, data types, positive order
identifiers, non-negative amounts, valid customer references, allowed
operations, and timezone-aware ISO-8601 timestamps.

Rejected records are stored in quarantine_records with their source
record and error reason.

Repeated identical rejected records with the same error reason are
deduplicated by application logic.

## 9. Transaction and Recovery Strategy

Target changes, event-history entries, processed-event identifiers,
quarantine inserts, and watermark changes are handled within a database
transaction.

If an exception occurs during processing, the transaction is rolled back.

The pipeline then records the failed execution and its error message
separately, so the failure remains observable.

A subsequent retry can process the source again without retaining
partially committed target changes from the failed transaction.

## 10. Observability

The pipeline_runs table records:

- Run identifier.
- Start and end timestamps.
- Execution status.
- Input, output, and rejected record counts.
- Error message when execution fails.

Application logs are written to reports/pipeline.log.

The reconciliation report records local execution evidence and
database counts.

## 11. Important Limitations

- The current source reader supports JSON files, not live database or API
  ingestion.
- The pipeline reads the JSON input before applying the watermark filter;
  it is not a source-side incremental query.
- A fixed customer reference set is configured in Python.
- Schema validation rejects unexpected fields; automatic schema evolution
  is not implemented.
- The watermark can advance past timestamped records that are rejected
  during validation. Such records may require explicit replay or
  remediation if they are not corrected within the lookback window.
- The lookback period is configurable but does not guarantee capture of
  events arriving later than that period.
- SQLite is intended for local demonstration and testing, not as a
  distributed production database.
- Database schema migrations and automated retention policies are not
  implemented.
- Performance results from this local sample are functional test evidence,
  not production-scale benchmarks.

## 12. Future Improvements

Potential extensions include:

- Support for SQL databases, APIs, and cloud storage sources.
- Configurable schema evolution and migration handling.
- Externalized customer reference data.
- Explicit replay of quarantined records.
- Larger synthetic data generation and performance benchmarking.
- Cloud deployment using Azure Data Factory, Azure Data Lake Storage,
  and Azure Databricks.
- Monitoring dashboards and operational alerting.
