import sqlite3

connection = sqlite3.connect("data/output/ingestion.db")

tables = connection.execute("""
SELECT name
FROM sqlite_master
WHERE type = 'table'
AND name NOT LIKE 'sqlite_%'
ORDER BY name
""").fetchall()

for table in tables:
    table_name = table[0]
    print("\nTABLE:", table_name)
    print("COLUMN | TYPE | NOT NULL | PRIMARY KEY")

    columns = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    for column in columns:
        print(column[1], "|", column[2], "|", column[3], "|", column[5])

connection.close()
