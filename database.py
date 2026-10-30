
import sqlite3
from datetime import datetime
from pathlib import Path


# Keep the database in the same folder as this file
DATABASE_PATH = Path(__file__).resolve().parent / "bmi_records.db"


# Connect to database
def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# Create database and table
def create_table():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                weight REAL,
                height REAL,
                bmi REAL,
                category TEXT,
                date TEXT
            )
        """)

        # Support older databases that may not have a name column
        cursor.execute("PRAGMA table_info(bmi_records)")
        columns = [column[1] for column in cursor.fetchall()]

        if "name" not in columns:
            cursor.execute(
                "ALTER TABLE bmi_records ADD COLUMN name TEXT"
            )


# Save BMI record
def save_record(name, weight, height, bmi, category):

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            weight,
            height,
            bmi,
            category,
            date
        ))


# Get all records in alphabetical order
def get_records():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, weight, height, bmi, category, date
            FROM bmi_records
            ORDER BY name COLLATE NOCASE ASC, id ASC
        """)

        return cursor.fetchall()


# Get BMI history for graph in chronological order
def get_bmi_history():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT bmi, date
            FROM bmi_records
            ORDER BY id ASC
        """)

        return cursor.fetchall()


# Delete a record using its database ID
def delete_record(record_id):

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM bmi_records WHERE id = ?",
            (record_id,)
        )

        return cursor.rowcount


# Get total number of records
def get_total_records():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM bmi_records"
        )

        return cursor.fetchone()[0]
