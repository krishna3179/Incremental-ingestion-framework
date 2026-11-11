
from datetime import datetime, timezone


def load_records(connection, records, run_id, source_file=None):
    """
    Load validated events into SQLite.

    The caller controls the transaction and commits only
    after the complete pipeline operation succeeds.
    """

    metrics = {
        "inserted": 0,
        "updated": 0,
        "deleted": 0,
        "stale": 0,
        "duplicates": 0,
        "processed": 0,
    }

    # Process events in source timestamp order.
    sorted_records = sorted(
        records,
        key=lambda record: record["source_updated_at"]
    )

    for record in sorted_records:
        event_id = record["event_id"]

        # Skip previously processed events.
        existing_event = connection.execute(
            "SELECT 1 FROM processed_events WHERE event_id = ?",
            (event_id,)
        ).fetchone()

        if existing_event:
            metrics["duplicates"] += 1
            continue

        order_id = record["order_id"]

        # Check whether the order already exists.
        existing_order = connection.execute(
            """
            SELECT source_updated_at
            FROM orders
            WHERE order_id = ?
            """,
            (order_id,)
        ).fetchone()

        # Preserve every new event in the history table.
        connection.execute(
            """
            INSERT INTO order_history (
                event_id,
                order_id,
                customer_id,
                amount,
                status,
                source_updated_at,
                operation,
                source_file
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                order_id,
                record["customer_id"],
                record["amount"],
                record["status"],
                record["source_updated_at"],
                record["operation"],
                source_file,
            )
        )

        # A newer event replaces the current order state.
        is_deleted = 1 if record["operation"] == "DELETE" else 0

        connection.execute(
            """
            INSERT INTO orders (
                order_id,
                customer_id,
                amount,
                status,
                source_updated_at,
                is_deleted,
                last_run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(order_id)
            DO UPDATE SET
                customer_id = excluded.customer_id,
                amount = excluded.amount,
                status = excluded.status,
                source_updated_at = excluded.source_updated_at,
                is_deleted = excluded.is_deleted,
                last_run_id = excluded.last_run_id

            WHERE excluded.source_updated_at > orders.source_updated_at
            """,
            (
                order_id,
                record["customer_id"],
                record["amount"],
                record["status"],
                record["source_updated_at"],
                is_deleted,
                run_id,
            )
        )

        # Record the event so a rerun cannot apply it twice.
        connection.execute(
            """
            INSERT INTO processed_events (event_id, processed_at)
            VALUES (?, ?)
            """,
            (
                event_id,
                datetime.now(timezone.utc).isoformat(),
            )
        )

        metrics["processed"] += 1

        if existing_order is None:
            if is_deleted:
                metrics["deleted"] += 1
            else:
                metrics["inserted"] += 1

        elif record["source_updated_at"] > existing_order["source_updated_at"]:
            if is_deleted:
                metrics["deleted"] += 1
            else:
                metrics["updated"] += 1

        else:
            metrics["stale"] += 1

    return metrics
