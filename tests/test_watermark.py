
import sqlite3

from src.watermark import (
    get_extraction_start,
    calculate_next_watermark,
    update_watermark,
)


def test_first_run_has_no_extraction_start():
    assert get_extraction_start(None) is None


def test_lookback_window():
    watermark = "2026-11-10T12:00:00+00:00"

    result = get_extraction_start(watermark, 60)

    assert result == "2026-11-10T11:00:00+00:00"


def test_calculate_latest_watermark():
    records = [
        {"source_updated_at": "2026-11-10T09:00:00+00:00"},
        {"source_updated_at": "2026-11-10T12:00:00+00:00"},
        {"source_updated_at": "2026-11-10T10:00:00+00:00"},
    ]

    result = calculate_next_watermark(records)

    assert result == "2026-11-10T12:00:00+00:00"


def test_watermark_never_moves_backwards():
    records = [
        {"source_updated_at": "2026-11-10T09:00:00+00:00"}
    ]

    current = "2026-11-10T12:00:00+00:00"

    result = calculate_next_watermark(records, current)

    assert result == current


def test_update_watermark_in_database():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE pipeline_watermarks (
            source_name TEXT PRIMARY KEY,
            last_watermark TEXT
        )
    """)

    update_watermark(
        connection,
        "orders",
        "2026-11-10T12:00:00+00:00"
    )

    result = connection.execute(
        "SELECT last_watermark FROM pipeline_watermarks "
        "WHERE source_name = ?",
        ("orders",)
    ).fetchone()

    assert result[0] == "2026-11-10T12:00:00+00:00"

    connection.close()
