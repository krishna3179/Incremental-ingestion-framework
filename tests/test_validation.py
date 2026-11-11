
from src.source_reader import read_source_file
from src.validator import validate_records


def test_sample_data_validation():
    records = read_source_file("data/sample/orders_sample.json")

    valid, rejected = validate_records(records)

    print("\nValid records:", len(valid))
    print("Rejected records:", len(rejected))

    assert len(valid) + len(rejected) == len(records)
    assert len(rejected) >= 1


def test_missing_customer_is_rejected():
    record = {
        "event_id": "test-001",
        "order_id": 1,
        "customer_id": None,
        "amount": 100,
        "status": "CREATED",
        "source_updated_at": "2026-11-10T09:00:00+00:00",
        "operation": "INSERT",
    }

    errors = validate_records([record])[1]

    assert len(errors) == 1




from src.validator import validate_record


def test_negative_amount_is_rejected():
    record = {
        "event_id": "test-002",
        "order_id": 2,
        "customer_id": 100,
        "amount": -500,
        "status": "CREATED",
        "source_updated_at": "2026-11-10T09:00:00+00:00",
        "operation": "INSERT",
    }

    errors = validate_record(record)

    assert "amount cannot be negative" in errors


def test_invalid_customer_reference():
    record = {
        "event_id": "test-003",
        "order_id": 3,
        "customer_id": 999,
        "amount": 500,
        "status": "CREATED",
        "source_updated_at": "2026-11-10T09:00:00+00:00",
        "operation": "INSERT",
    }

    errors = validate_record(record)

    assert "Invalid customer reference: 999" in errors


def test_invalid_timestamp():
    record = {
        "event_id": "test-004",
        "order_id": 4,
        "customer_id": 100,
        "amount": 500,
        "status": "CREATED",
        "source_updated_at": "invalid-date",
        "operation": "INSERT",
    }

    errors = validate_record(record)

    assert any("ISO-8601" in error for error in errors)


def test_missing_required_field():
    record = {
        "event_id": "test-005",
        "order_id": 5,
        "customer_id": 100,
        "amount": 500,
        "status": "CREATED",
        "source_updated_at": "2026-11-10T09:00:00+00:00",
    }

    errors = validate_record(record)

    assert any("Missing required fields" in error for error in errors)
