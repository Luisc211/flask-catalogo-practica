import sqlite3

DB_NAME = "catalogo.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL
    )""")
    cantidad = conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0]
    if cantidad == 0:
        conn.executemany(
            "INSERT INTO productos (nombre, precio) VALUES (?, ?)",
            [("Cuaderno", 5000), ("Lapicero", 1500), ("Borrador", 800)],
        )
    conn.commit()
    conn.close()
