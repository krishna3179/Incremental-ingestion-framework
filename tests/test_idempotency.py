
import sqlite3

from src.loader import load_records


def create_test_database():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.executescript("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            source_updated_at TEXT NOT NULL,
            is_deleted INTEGER DEFAULT 0,
            last_run_id TEXT
        );

        CREATE TABLE order_history (
            event_id TEXT PRIMARY KEY,
            order_id INTEGER NOT NULL,
            customer_id INTEGER,
            amount REAL,
            status TEXT,
            source_updated_at TEXT NOT NULL,
            operation TEXT NOT NULL,
            source_file TEXT
        );

        CREATE TABLE processed_events (
            event_id TEXT PRIMARY KEY,
            processed_at TEXT NOT NULL
        );
    """)

    return connection


def sample_event():
    return {
        "event_id": "event-001",
        "order_id": 1,
        "customer_id": 100,
        "amount": 500.0,
        "status": "CREATED",
        "source_updated_at": "2026-11-10T09:00:00+00:00",
        "operation": "INSERT",
    }


def test_rerun_does_not_duplicate_order():
    connection = create_test_database()
    event = sample_event()

    with connection:
        first = load_records(connection, [event], "run-001")

    with connection:
        second = load_records(connection, [event], "run-002")

    order_count = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    history_count = connection.execute(
        "SELECT COUNT(*) FROM order_history"
    ).fetchone()[0]

    assert first["inserted"] == 1
    assert second["duplicates"] == 1
    assert order_count == 1
    assert history_count == 1

    connection.close()
