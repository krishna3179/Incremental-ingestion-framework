
from datetime import datetime, timedelta, timezone


def parse_timestamp(value):
    """Convert an ISO-8601 timestamp into UTC."""

    timestamp = datetime.fromisoformat(value)

    if timestamp.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")

    return timestamp.astimezone(timezone.utc)


def get_extraction_start(last_watermark, lookback_minutes=1440):
    """
    Calculate the extraction starting point.

    First run: return None.
    Later runs: subtract the lookback period.
    """

    if last_watermark is None:
        return None

    watermark_time = parse_timestamp(last_watermark)

    extraction_start = watermark_time - timedelta(
        minutes=lookback_minutes
    )

    return extraction_start.isoformat()


def calculate_next_watermark(records, current_watermark=None):
    """Find the latest timestamp among validated records."""

    timestamps = [
        parse_timestamp(record["source_updated_at"])
        for record in records
    ]

    if not timestamps:
        return current_watermark

    latest_timestamp = max(timestamps)

    if current_watermark is not None:
        latest_timestamp = max(
            latest_timestamp,
            parse_timestamp(current_watermark)
        )

    return latest_timestamp.isoformat()


def update_watermark(connection, source_name, new_watermark):
    """
    Insert or update a source watermark.

    The caller controls the transaction and commits only
    after the target data has been successfully processed.
    """

    connection.execute(
        """
        INSERT INTO pipeline_watermarks (
            source_name,
            last_watermark
        )
        VALUES (?, ?)
        ON CONFLICT(source_name)
        DO UPDATE SET last_watermark = excluded.last_watermark
        """,
        (source_name, new_watermark)
    )
