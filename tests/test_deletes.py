
from tests.test_idempotency import create_test_database
from src.loader import load_records


def make_event(event_id, timestamp, operation, amount, status):
    return {
        "event_id": event_id,
        "order_id": 1,
        "customer_id": 100,
        "amount": amount,
        "status": status,
        "source_updated_at": timestamp,
        "operation": operation,
    }


def test_update_existing_order():
    connection = create_test_database()

    first = make_event(
        "event-001",
        "2026-11-10T09:00:00+00:00",
        "INSERT",
        500,
        "CREATED",
    )

    second = make_event(
        "event-002",
        "2026-11-10T10:00:00+00:00",
        "UPDATE",
        800,
        "UPDATED",
    )

    with connection:
        load_records(connection, [first], "run-001")

    with connection:
        metrics = load_records(connection, [second], "run-002")

    order = connection.execute(
        "SELECT amount, status FROM orders WHERE order_id = 1"
    ).fetchone()

    assert order["amount"] == 800
    assert order["status"] == "UPDATED"
    assert metrics["updated"] == 1

    connection.close()


def test_delete_order_soft_delete():
    connection = create_test_database()

    insert_event = make_event(
        "event-003",
        "2026-11-10T09:00:00+00:00",
        "INSERT",
        500,
        "CREATED",
    )

    delete_event = make_event(
        "event-004",
        "2026-11-10T10:00:00+00:00",
        "DELETE",
        0,
        "DELETED",
    )

    with connection:
        load_records(connection, [insert_event], "run-001")

    with connection:
        metrics = load_records(connection, [delete_event], "run-002")

    order = connection.execute(
        "SELECT is_deleted FROM orders WHERE order_id = 1"
    ).fetchone()

    assert order["is_deleted"] == 1
    assert metrics["deleted"] == 1

    connection.close()


def test_late_event_does_not_overwrite_newer_data():
    connection = create_test_database()

    newer_event = make_event(
        "event-005",
        "2026-11-10T12:00:00+00:00",
        "UPDATE",
        900,
        "UPDATED",
    )

    late_event = make_event(
        "event-006",
        "2026-11-10T10:00:00+00:00",
        "UPDATE",
        600,
        "UPDATED",
    )

    with connection:
        load_records(connection, [newer_event], "run-001")

    with connection:
        metrics = load_records(connection, [late_event], "run-002")

    order = connection.execute(
        "SELECT amount FROM orders WHERE order_id = 1"
    ).fetchone()

    assert order["amount"] == 900
    assert metrics["stale"] == 1

    connection.close()
