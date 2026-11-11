
import csv
import random
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import uuid


random.seed(42)

OUTPUT_DIR = Path("data/sample")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_TIME = datetime(2026, 11, 10, 9, 0, 0, tzinfo=timezone.utc)


def generate_event(order_id, customer_id, amount, status,
                   minutes_offset, operation="INSERT"):

    updated_at = BASE_TIME + timedelta(minutes=minutes_offset)

    event = {
        "event_id": str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"order-{order_id}-{updated_at.isoformat()}-{operation}"
        )),
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "status": status,
        "source_updated_at": updated_at.isoformat(),
        "operation": operation
    }

    return event


def generate_sample_data():

    events = []

    # Initial orders
    for order_id in range(1, 11):
        events.append(
            generate_event(
                order_id,
                random.randint(100, 105),
                round(random.uniform(100, 5000), 2),
                "CREATED",
                order_id * 10
            )
        )

    # Update an existing order
    events.append(
        generate_event(1, 101, 2500.00, "UPDATED", 150, "UPDATE")
    )

    # Delete an existing order
    events.append(
        generate_event(2, 102, 0, "DELETED", 160, "DELETE")
    )

    # Late-arriving record with an older source timestamp
    events.append(
        generate_event(11, 103, 1200.00, "CREATED", 25)
    )

    # Duplicate event
    events.append(events[0].copy())

    # Invalid: missing customer ID
    invalid_1 = generate_event(
        12, None, 800, "CREATED", 180
    )
    events.append(invalid_1)

    # Invalid: negative amount
    invalid_2 = generate_event(
        13, 104, -500, "CREATED", 190
    )
    events.append(invalid_2)

    # Invalid: missing order ID
    invalid_3 = generate_event(
        None, 105, 700, "CREATED", 200
    )
    events.append(invalid_3)

    random.shuffle(events)

    output_file = OUTPUT_DIR / "orders_sample.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=4)

    print(f"Generated {len(events)} events")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    generate_sample_data()
