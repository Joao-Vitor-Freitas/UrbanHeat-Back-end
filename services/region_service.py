from database.connection import get_connection


def create_region(name: str):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO regions(name)
        VALUES(?)
        """,
        (name,),
    )

    conn.commit()
    conn.close()


def get_regions():

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT id, name
        FROM regions
        ORDER BY name
        """
    )

    regions = cursor.fetchall()

    conn.close()

    return regions
