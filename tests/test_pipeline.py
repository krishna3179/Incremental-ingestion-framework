
import json

from src.pipeline import run_pipeline
from src.database import get_connection


def write_valid_source(path):
    records = [
        {
            "event_id": "test-event-001",
            "order_id": 501,
            "customer_id": 100,
            "amount": 500.00,
            "status": "CREATED",
            "source_updated_at": "2026-11-10T10:00:00+00:00",
            "operation": "INSERT",
        }
    ]

    path.write_text(json.dumps(records), encoding="utf-8")


def test_pipeline_success_and_idempotent_rerun(tmp_path, monkeypatch):
    from src import database

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    source_file = tmp_path / "orders.json"
    write_valid_source(source_file)

    first_run = run_pipeline(str(source_file))

    assert first_run["status"] == "SUCCESS"
    assert first_run["inserted"] == 1

    second_run = run_pipeline(str(source_file))

    assert second_run["status"] == "SUCCESS"
    assert second_run["duplicates"] == 1

    connection = get_connection()

    assert connection.execute(
        "SELECT COUNT(*) FROM orders WHERE order_id = 501"
    ).fetchone()[0] == 1

    assert connection.execute(
        "SELECT COUNT(*) FROM order_history WHERE order_id = 501"
    ).fetchone()[0] == 1

    connection.close()


def test_failure_after_load_rolls_back_data(tmp_path, monkeypatch):
    from src import database

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "failure.db",
    )

    source_file = tmp_path / "orders.json"
    write_valid_source(source_file)

    result = run_pipeline(
        source_file=str(source_file),
        fail_after_load=True,
    )

    assert result["status"] == "FAILED"

    connection = get_connection()

    assert connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0] == 0

    assert connection.execute(
        "SELECT COUNT(*) FROM order_history"
    ).fetchone()[0] == 0

    assert connection.execute(
        "SELECT COUNT(*) FROM processed_events"
    ).fetchone()[0] == 0

    assert connection.execute(
        "SELECT COUNT(*) FROM pipeline_watermarks"
    ).fetchone()[0] == 0

    connection.close()


def test_malformed_json_does_not_change_watermark(
    tmp_path,
    monkeypatch,
):
    from src import database

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "malformed.db",
    )

    valid_file = tmp_path / "valid.json"
    write_valid_source(valid_file)

    first_result = run_pipeline(str(valid_file))
    assert first_result["status"] == "SUCCESS"

    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text(
        '[{"event_id": "broken",}]',
        encoding="utf-8",
    )

    result = run_pipeline(str(malformed_file))

    assert result["status"] == "FAILED"

    connection = get_connection()

    watermark = connection.execute(
        "SELECT last_watermark FROM pipeline_watermarks"
    ).fetchone()[0]

    assert watermark == "2026-11-10T10:00:00+00:00"

    assert connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0] == 1

    connection.close()
