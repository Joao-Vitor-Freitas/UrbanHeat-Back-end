from database.connection import get_connection


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sensor_code TEXT NOT NULL UNIQUE,
        region_id INTEGER NOT NULL,

        FOREIGN KEY(region_id)
            REFERENCES regions(id)
            ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sensor_id INTEGER NOT NULL,

        temperature REAL NOT NULL,
        humidity REAL NOT NULL,

        created_at DATETIME NOT NULL,

        FOREIGN KEY(sensor_id)
            REFERENCES sensors(id)
            ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS heat_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        region_id INTEGER NOT NULL,

        score REAL NOT NULL,
        classification TEXT NOT NULL,

        average_temperature REAL NOT NULL,
        high_temperature_frequency REAL NOT NULL,
        critical_duration REAL NOT NULL,

        created_at DATETIME NOT NULL,

        FOREIGN KEY(region_id)
            REFERENCES regions(id)
            ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
