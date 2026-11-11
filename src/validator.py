
from datetime import datetime
from src.config import (
    REQUIRED_FIELDS,
    ALLOWED_OPERATIONS,
    VALID_CUSTOMER_IDS,
)


def validate_record(record):
    errors = []

    # Check required fields
    missing_fields = REQUIRED_FIELDS - set(record.keys())

    if missing_fields:
        errors.append(
            f"Missing required fields: {sorted(missing_fields)}"
        )
        return errors

    # Check unexpected fields (schema drift)
    unexpected_fields = set(record.keys()) - REQUIRED_FIELDS

    if unexpected_fields:
        errors.append(
            f"Unexpected fields: {sorted(unexpected_fields)}"
        )

    # Validate event ID
    if not isinstance(record["event_id"], str) or not record["event_id"].strip():
        errors.append("event_id must be a non-empty string")

    # Validate order ID
    order_id = record["order_id"]

    if isinstance(order_id, bool) or not isinstance(order_id, int):
        errors.append("order_id must be an integer")
    elif order_id <= 0:
        errors.append("order_id must be positive")

    # Validate customer ID
    customer_id = record["customer_id"]

    if isinstance(customer_id, bool) or not isinstance(customer_id, int):
        errors.append("customer_id must be an integer")
    elif customer_id not in VALID_CUSTOMER_IDS:
        errors.append(f"Invalid customer reference: {customer_id}")

    # Validate amount
    amount = record["amount"]

    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        errors.append("amount must be numeric")
    elif amount < 0:
        errors.append("amount cannot be negative")

    # Validate status
    if not isinstance(record["status"], str) or not record["status"].strip():
        errors.append("status must be a non-empty string")

    # Validate operation
    if record["operation"] not in ALLOWED_OPERATIONS:
        errors.append("Invalid operation")

    # Validate timestamp
    try:
        timestamp = datetime.fromisoformat(record["source_updated_at"])

        if timestamp.tzinfo is None:
            errors.append("source_updated_at must include a timezone")

    except (TypeError, ValueError):
        errors.append("source_updated_at must be a valid ISO-8601 timestamp")

    return errors


def validate_records(records):
    valid_records = []
    rejected_records = []
    seen_event_ids = set()

    for record in records:
        if not isinstance(record, dict):
            rejected_records.append({
                "record": record,
                "errors": ["Each event must be a JSON object"],
            })
            continue

        errors = validate_record(record)

        event_id = record.get("event_id")

        if isinstance(event_id, str) and event_id:
            if event_id in seen_event_ids:
                errors.append(f"Duplicate event_id: {event_id}")
            else:
                seen_event_ids.add(event_id)

        if errors:
            rejected_records.append({
                "record": record,
                "errors": errors,
            })
        else:
            valid_records.append(record)

    return valid_records, rejected_records
