# Reconciliation and Execution Evidence

## Automated tests

- Test framework: pytest
- Python version: 3.12.10
- Total tests: 18
- Passed: 18
- Failed: 0

## Current local database snapshot

| Metric | Count |
|---|---:|
| Orders table rows | 12 |
| Order history events | 17 |
| Processed events | 17 |
| Quarantined records | 4 |
| Pipeline runs | 15 |
| Successful runs | 10 |
| Failed runs | 5 |

## Watermark

- Source: orders
- Last watermark: 2026-11-10T12:20:00+00:00

## Verified scenarios

- Initial ingestion
- Same-input rerun without duplicate target records
- Late-arriving event within the lookback window
- Newer update applied successfully
- Older update prevented from overwriting newer data
- Soft delete
- Malformed JSON detected and recorded as a failed run
- Simulated failure after loading rolled back target changes
- Quarantine records deduplicated across repeated runs

## Notes

The database counts represent the local development and testing database,
including records created by manual test scenarios. Pipeline run totals
include successful and deliberately failed test executions.

These are functional test results, not production-scale performance
benchmarks.

## Order reconciliation

| Order metric | Count |
|---|---:|
| Total order records | 12 |
| Active orders | 10 |
| Soft-deleted orders | 2 |
| Soft-deleted order IDs | 2, 14 |

Soft deletes preserve order records for history and audit purposes.
