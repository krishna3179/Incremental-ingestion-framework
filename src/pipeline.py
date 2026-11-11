
import uuid
from datetime import datetime, timezone

from src.database import create_tables, get_connection
from src.source_reader import read_source_file
from src.validator import validate_records
from src.loader import load_records
from src.quarantine import save_rejected_records
from src.watermark import (
    calculate_next_watermark,
    get_extraction_start,
    parse_timestamp,
    update_watermark,
)
from src.logger import logger


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def run_pipeline(
    source_file="data/sample/orders_sample.json",
    source_name="orders",
    lookback_minutes=1440,
    fail_after_load=False,
):
    create_tables()
    connection = get_connection()

    run_id = str(uuid.uuid4())
    start_time = utc_now()

    try:
        # Record the pipeline run separately so failures are visible.
        connection.execute(
            """
            INSERT INTO pipeline_runs
            (run_id, start_time, status)
            VALUES (?, ?, ?)
            """,
            (run_id, start_time, "RUNNING"),
        )
        connection.commit()

        logger.info("Pipeline started. Run ID: %s", run_id)

        # Begin the main data transaction.
        connection.execute("BEGIN IMMEDIATE")

        # Read source events.
        records = read_source_file(source_file)

        # Retrieve the previous watermark.
        watermark_row = connection.execute(
            """
            SELECT last_watermark
            FROM pipeline_watermarks
            WHERE source_name = ?
            """,
            (source_name,),
        ).fetchone()

        previous_watermark = (
            watermark_row["last_watermark"] if watermark_row else None
        )

        # Calculate extraction start with lookback.
        extraction_start = get_extraction_start(
            previous_watermark,
            lookback_minutes,
        )

        # Select records within the extraction window.
        selected_records = []

        for record in records:
            timestamp_value = record.get("source_updated_at")

            try:
                event_time = parse_timestamp(timestamp_value)

                if extraction_start is not None:
                    if event_time < parse_timestamp(extraction_start):
                        continue

                selected_records.append(record)

            except (TypeError, ValueError):
                # Keep invalid timestamps so validation can quarantine them.
                selected_records.append(record)

        # Validate source records.
        valid_records, rejected_records = validate_records(selected_records)

        # Load valid records into target tables.
        load_metrics = load_records(
            connection,
            valid_records,
            run_id,
            source_file,
        )

        # Simulate failure to test transaction rollback.
        if fail_after_load:
            raise RuntimeError(
                "Simulated failure after loading records"
            )

        # Save only new quarantine entries.
        quarantine_inserted = save_rejected_records(
            connection,
            rejected_records,
            run_id,
            source_file,
        )

        # Count all rejected records, including previously quarantined ones.
        rejected_count = len(rejected_records)

        # Calculate watermark from records with valid timestamps.
        timestamped_records = []

        for record in selected_records:
            try:
                parse_timestamp(record["source_updated_at"])
                timestamped_records.append(record)
            except (KeyError, TypeError, ValueError):
                continue

        new_watermark = calculate_next_watermark(
            timestamped_records,
            previous_watermark,
        )

        # Update watermark within the same transaction.
        if new_watermark is not None:
            update_watermark(
                connection,
                source_name,
                new_watermark,
            )

        # Mark the run successful.
        connection.execute(
            """
            UPDATE pipeline_runs
            SET end_time = ?,
                status = ?,
                input_count = ?,
                output_count = ?,
                rejected_count = ?
            WHERE run_id = ?
            """,
            (
                utc_now(),
                "SUCCESS",
                len(selected_records),
                load_metrics["processed"],
                rejected_count,
                run_id,
            ),
        )

        # Commit target data, quarantine records and watermark together.
        connection.commit()

        logger.info(
            "Pipeline completed. Run ID: %s | Metrics: %s",
            run_id,
            load_metrics,
        )

        return {
            "run_id": run_id,
            "status": "SUCCESS",
            "input_count": len(selected_records),
            "valid_count": len(valid_records),
            "rejected_count": rejected_count,
            "quarantine_inserted": quarantine_inserted,
            "watermark": new_watermark,
            **load_metrics,
        }

    except Exception as error:
        # Roll back all changes in the main data transaction.
        connection.rollback()

        # Record the failure outside the rolled-back transaction.
        connection.execute(
            """
            UPDATE pipeline_runs
            SET end_time = ?,
                status = ?,
                error_message = ?
            WHERE run_id = ?
            """,
            (
                utc_now(),
                "FAILED",
                str(error),
                run_id,
            ),
        )

        connection.commit()

        logger.exception(
            "Pipeline failed. Run ID: %s",
            run_id,
        )

        return {
            "run_id": run_id,
            "status": "FAILED",
            "error": str(error),
        }

    finally:
        connection.close()


if __name__ == "__main__":
    result = run_pipeline()

    print("\n========== PIPELINE RESULT ==========")

    for key, value in result.items():
        print(f"{key}: {value}")
