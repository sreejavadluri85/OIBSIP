import sqlite3
from datetime import datetime
from pathlib import Path


# ==========================================
# DATABASE PATH
# ==========================================

DATABASE_PATH = Path(__file__).resolve().parent / "bmi_records.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# CREATE / UPDATE TABLE
# ==========================================

def create_table():

    with get_connection() as connection:

        cursor = connection.cursor()


        # Create the table for new installations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT,

                age INTEGER,

                gender TEXT,

                age_group TEXT,

                weight REAL,

                height REAL,

                bmi REAL,

                category TEXT,

                date TEXT

            )
        """)


        # ==========================================
        # SUPPORT OLD DATABASES
        # ==========================================

        cursor.execute("PRAGMA table_info(bmi_records)")

        existing_columns = [
            column["name"]
            for column in cursor.fetchall()
        ]


        # Add missing columns automatically

        if "name" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN name TEXT
            """)


        if "age" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN age INTEGER
            """)


        if "gender" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN gender TEXT
            """)


        if "age_group" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN age_group TEXT
            """)


        if "weight" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN weight REAL
            """)


        if "height" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN height REAL
            """)


        if "bmi" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN bmi REAL
            """)


        if "category" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN category TEXT
            """)


        if "date" not in existing_columns:

            cursor.execute("""
                ALTER TABLE bmi_records
                ADD COLUMN date TEXT
            """)


# ==========================================
# SAVE BMI RECORD
# ==========================================

def save_record(
    name,
    age,
    gender,
    age_group,
    weight,
    height,
    bmi,
    category
):

    date = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            INSERT INTO bmi_records (

                name,
                age,
                gender,
                age_group,
                weight,
                height,
                bmi,
                category,
                date

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            name,
            age,
            gender,
            age_group,
            weight,
            height,
            bmi,
            category,
            date

        ))


# ==========================================
# GET ALL BMI RECORDS
# ==========================================

def get_records():

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            SELECT

                id,
                name,
                age,
                gender,
                age_group,
                weight,
                height,
                bmi,
                category,
                date

            FROM bmi_records

            ORDER BY id DESC
        """)


        return cursor.fetchall()


# ==========================================
# GET LATEST BMI RECORD
# ==========================================

def get_latest_record():

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            SELECT

                id,
                name,
                age,
                gender,
                age_group,
                weight,
                height,
                bmi,
                category,
                date

            FROM bmi_records

            ORDER BY id DESC

            LIMIT 1
        """)


        return cursor.fetchone()


# ==========================================
# GET BMI HISTORY FOR GRAPH
# ==========================================

def get_bmi_history():

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            SELECT

                id,
                name,
                bmi,
                date

            FROM bmi_records

            ORDER BY id ASC
        """)


        return cursor.fetchall()


# ==========================================
# GET WEIGHT HISTORY
# ==========================================

def get_weight_history():

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            SELECT

                id,
                name,
                weight,
                date

            FROM bmi_records

            ORDER BY id ASC
        """)


        return cursor.fetchall()


# ==========================================
# DELETE BMI RECORD
# ==========================================

def delete_record(record_id):

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            DELETE FROM bmi_records
            WHERE id = ?
        """, (record_id,))


        return cursor.rowcount


# ==========================================
# GET TOTAL RECORDS
# ==========================================

def get_total_records():

    with get_connection() as connection:

        cursor = connection.cursor()


        cursor.execute("""
            SELECT COUNT(*)
            FROM bmi_records
        """)


        return cursor.fetchone()[0]


# ==========================================
# WATER TRACKER TABLE
# ==========================================

def create_water_table():

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_records (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                water_count INTEGER DEFAULT 0,

                date TEXT UNIQUE

            )
        """)

# ==========================================
# GET TODAY'S WATER INTAKE
# ==========================================

def get_today_water():

    today = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT water_count
            FROM water_records
            WHERE date = ?
        """, (today,))

        record = cursor.fetchone()

        if record:

            return record["water_count"]

        return 0

# ==========================================
# SAVE / UPDATE TODAY'S WATER INTAKE
# ==========================================

def save_today_water(water_count):

    today = datetime.now().strftime("%Y-%m-%d")

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM water_records
            WHERE date = ?
        """, (today,))

        record = cursor.fetchone()


        if record:

            cursor.execute("""
                UPDATE water_records

                SET water_count = ?

                WHERE date = ?
            """, (
                water_count,
                today
            ))

        else:

            cursor.execute("""
                INSERT INTO water_records (
                    water_count,
                    date
                )

                VALUES (?, ?)
            """, (
                water_count,
                today
            ))