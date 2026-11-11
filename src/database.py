
import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/output/ingestion.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enable foreign-key enforcement for this connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    connection = get_connection()

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                source_updated_at TEXT NOT NULL,
                is_deleted INTEGER DEFAULT 0,
                last_run_id TEXT
            );

            CREATE TABLE IF NOT EXISTS order_history (
                event_id TEXT PRIMARY KEY,
                order_id INTEGER NOT NULL,
                customer_id INTEGER,
                amount REAL,
                status TEXT,
                source_updated_at TEXT NOT NULL,
                operation TEXT NOT NULL,
                source_file TEXT
            );

            CREATE TABLE IF NOT EXISTS pipeline_watermarks (
                source_name TEXT PRIMARY KEY,
                last_watermark TEXT
            );

            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT NOT NULL,
                input_count INTEGER DEFAULT 0,
                output_count INTEGER DEFAULT 0,
                rejected_count INTEGER DEFAULT 0,
                error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS quarantine_records (
                quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                source_file TEXT,
                source_record TEXT NOT NULL,
                error_reason TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS processed_events (
                event_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_orders_updated_at
            ON orders(source_updated_at);

            CREATE INDEX IF NOT EXISTS idx_history_order_id
            ON order_history(order_id);

            CREATE INDEX IF NOT EXISTS idx_quarantine_run_id
            ON quarantine_records(run_id);
        """)

        connection.commit()
        print("Database tables and indexes created successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()

    connection = get_connection()

    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print("\nCreated tables:")

    for table in tables:
        print(table["name"])

    connection.close()
