
import json


def canonical_json(value):
    return json.dumps(value, sort_keys=True, default=str)


def deduplicate_quarantine(connection):
    rows = connection.execute(
        """
        SELECT quarantine_id, source_record, error_reason
        FROM quarantine_records
        ORDER BY quarantine_id
        """
    ).fetchall()

    seen = set()
    duplicate_ids = []

    for row in rows:
        record = json.loads(row["source_record"])
        key = (canonical_json(record), row["error_reason"])

        if key in seen:
            duplicate_ids.append(row["quarantine_id"])
        else:
            seen.add(key)

    if duplicate_ids:
        placeholders = ",".join("?" for _ in duplicate_ids)
        connection.execute(
            f"DELETE FROM quarantine_records WHERE quarantine_id IN ({placeholders})",
            duplicate_ids,
        )

    return len(duplicate_ids)


def save_rejected_records(connection, rejected_records, run_id, source_file=None):
    existing_rows = connection.execute(
        "SELECT source_record, error_reason FROM quarantine_records"
    ).fetchall()

    seen = {
        (canonical_json(json.loads(row["source_record"])), row["error_reason"])
        for row in existing_rows
    }

    inserted_count = 0

    for item in rejected_records:
        source_record = canonical_json(item["record"])
        error_reason = "; ".join(item["errors"])
        key = (source_record, error_reason)

        if key in seen:
            continue

        connection.execute(
            """
            INSERT INTO quarantine_records
            (run_id, source_file, source_record, error_reason)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, source_file, source_record, error_reason),
        )

        seen.add(key)
        inserted_count += 1

    return inserted_count
