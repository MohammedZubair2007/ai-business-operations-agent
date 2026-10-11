
import sqlite3
from pathlib import Path

# Find the root folder of our project
BASE_DIR = Path(__file__).resolve().parent.parent

# Store our database inside the data folder
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "business.db"


def get_connection(read_only=False):
    """Connect to the SQLite database."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if read_only:
        # Open the database in read-only mode
        connection = sqlite3.connect(
            f"{DB_PATH.resolve().as_uri()}?mode=ro",
            uri=True,
        )
        connection.execute("PRAGMA query_only = ON")
    else:
        connection = sqlite3.connect(DB_PATH)

    # Return query results as dictionary-like rows
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the database tables and insert sample data."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:

        # Table containing sales records
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_date TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                units_sold INTEGER NOT NULL,
                revenue REAL NOT NULL
            )
        """)

        # Table containing recommendations awaiting review
        conn.execute("""
            CREATE TABLE IF NOT EXISTS action_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                rationale TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert sample sales only if the table is empty
        count = conn.execute(
            "SELECT COUNT(*) FROM sales"
        ).fetchone()[0]

        if count == 0:
            sample_data = [
                # August 2026
                ("2026-08-05", "P001", "Wireless Mouse", 100, 2500),
                ("2026-08-15", "P001", "Wireless Mouse", 80, 2000),
                ("2026-08-10", "P002", "USB-C Hub", 80, 6400),
                ("2026-08-20", "P002", "USB-C Hub", 70, 5600),
                ("2026-08-12", "P003", "Laptop Stand", 50, 2500),
                ("2026-08-22", "P003", "Laptop Stand", 50, 2500),
                ("2026-08-14", "P004", "Keyboard", 60, 4800),
                ("2026-08-24", "P004", "Keyboard", 40, 3200),

                # September 2026
                ("2026-09-05", "P001", "Wireless Mouse", 50, 1250),
                ("2026-09-15", "P001", "Wireless Mouse", 40, 1000),
                ("2026-09-10", "P002", "USB-C Hub", 60, 4800),
                ("2026-09-20", "P002", "USB-C Hub", 50, 4000),
                ("2026-09-12", "P003", "Laptop Stand", 55, 2750),
                ("2026-09-22", "P003", "Laptop Stand", 55, 2750),
                ("2026-09-14", "P004", "Keyboard", 60, 4800),
                ("2026-09-24", "P004", "Keyboard", 60, 4800),
            ]

            conn.executemany("""
                INSERT INTO sales (
                    sale_date,
                    product_id,
                    product_name,
                    units_sold,
                    revenue
                )
                VALUES (?, ?, ?, ?, ?)
            """, sample_data)

        conn.commit()
