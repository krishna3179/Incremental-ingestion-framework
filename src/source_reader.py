
import json
from pathlib import Path


def read_source_file(file_path):
    """
    Read JSON events from a source file.
    Return a list of records.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            records = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON file: {error}")

    if not isinstance(records, list):
        raise ValueError("Source JSON must contain a list of events")

    return records


if __name__ == "__main__":
    data = read_source_file("data/sample/orders_sample.json")

    print("Total records:", len(data))
    print("\nFirst record:")
    print(data[0])
