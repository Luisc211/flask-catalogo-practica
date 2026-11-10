import sqlite3

DB_NAME = "catalogo.db"

CATEGORIAS_INICIALES = [
    ("Papelería", 500, 50_000),
    ("Tecnología", 20_000, 10_000_000),
    ("Hogar", 2_000, 2_000_000),
]

PRODUCTOS_INICIALES = [
    ("Cuaderno", 5000, "Papelería"),
    ("Lapicero", 1500, "Papelería"),
    ("Borrador", 1000, "Papelería"),
    ("Audífonos", 45000, "Tecnología"),
]


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            precio_min INTEGER NOT NULL,
            precio_max INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL,
            categoria_id INTEGER NOT NULL REFERENCES categorias(id)
        )
        """
    )

    if conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO categorias (nombre, precio_min, precio_max) VALUES (?, ?, ?)",
            CATEGORIAS_INICIALES,
        )

    if conn.execute("SELECT COUNT(*) FROM productos").fetchone()[0] == 0:
        conn.executemany(
            """
            INSERT INTO productos (nombre, precio, categoria_id)
            VALUES (?, ?, (SELECT id FROM categorias WHERE nombre = ?))
            """,
            PRODUCTOS_INICIALES,
        )

    conn.commit()
    conn.close()
