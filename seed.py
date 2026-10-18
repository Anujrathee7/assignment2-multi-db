"""Creates the three SQLite databases and fills them with dummy data.

Run directly (`python seed.py`) to reset every database to its original state.
"""
import os
import sqlite3

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SCHEMAS = {
    "library": """
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            year INTEGER,
            available INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            joined TEXT
        );
    """,
    "school": """
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER,
            email TEXT,
            gpa REAL
        );
        CREATE TABLE courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            teacher TEXT,
            credits INTEGER
        );
    """,
    "store": """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            order_date TEXT
        );
    """,
}

DUMMY_DATA = {
    "library": {
        "books": [
            ("To Kill a Mockingbird", "Harper Lee", "Fiction", 1960, 1),
            ("1984", "George Orwell", "Dystopian", 1949, 0),
            ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", 1925, 1),
            ("Sapiens", "Yuval Noah Harari", "History", 2011, 1),
            ("The Hobbit", "J.R.R. Tolkien", "Fantasy", 1937, 0),
            ("Clean Code", "Robert C. Martin", "Programming", 2008, 1),
            ("Dune", "Frank Herbert", "Sci-Fi", 1965, 1),
            ("Pride and Prejudice", "Jane Austen", "Classic", 1813, 1),
        ],
        "members": [
            ("Alice Johnson", "alice@example.com", "2023-01-14"),
            ("Brian Smith", "brian@example.com", "2023-03-02"),
            ("Chloe Davis", "chloe@example.com", "2024-06-21"),
            ("Daniel Lee", "daniel@example.com", "2024-09-10"),
            ("Emma Wilson", "emma@example.com", "2025-02-05"),
        ],
    },
    "school": {
        "students": [
            ("Liam Brown", 10, "liam@school.edu", 3.4),
            ("Olivia Garcia", 11, "olivia@school.edu", 3.9),
            ("Noah Martinez", 9, "noah@school.edu", 2.8),
            ("Ava Robinson", 12, "ava@school.edu", 3.6),
            ("Ethan Clark", 10, "ethan@school.edu", 3.1),
            ("Sophia Lewis", 11, "sophia@school.edu", 3.7),
        ],
        "courses": [
            ("MATH101", "Algebra I", "Mr. Turner", 4),
            ("SCI201", "Biology", "Ms. Patel", 4),
            ("ENG110", "English Literature", "Mrs. Hughes", 3),
            ("CS150", "Intro to Programming", "Mr. Nguyen", 3),
            ("HIS120", "World History", "Ms. Adams", 3),
        ],
    },
    "store": {
        "products": [
            ("Wireless Mouse", "Electronics", 24.99, 120),
            ("Mechanical Keyboard", "Electronics", 79.50, 45),
            ("Coffee Mug", "Kitchen", 9.99, 300),
            ("Desk Lamp", "Home", 34.00, 60),
            ("Notebook (A5)", "Stationery", 4.50, 500),
            ("Water Bottle", "Sports", 15.75, 150),
            ("USB-C Cable", "Electronics", 11.99, 250),
        ],
        "orders": [
            ("Alice Johnson", "Wireless Mouse", 2, "2026-09-01"),
            ("Marcus Hill", "Coffee Mug", 4, "2026-09-03"),
            ("Priya Shah", "Desk Lamp", 1, "2026-09-07"),
            ("Tom Becker", "Mechanical Keyboard", 1, "2026-09-12"),
            ("Alice Johnson", "Notebook (A5)", 10, "2026-09-15"),
            ("Sara Kim", "USB-C Cable", 3, "2026-09-20"),
        ],
    },
}


def db_path(name):
    return os.path.join(DATA_DIR, f"{name}.db")


def seed_database(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(db_path(name))
    for table in DUMMY_DATA[name]:
        conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.executescript(SCHEMAS[name])
    for table, rows in DUMMY_DATA[name].items():
        cols = [c[1] for c in conn.execute(f"PRAGMA table_info({table})")][1:]  # skip id
        placeholders = ", ".join("?" for _ in cols)
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", rows
        )
    conn.commit()
    conn.close()


def seed_all():
    for name in SCHEMAS:
        seed_database(name)


if __name__ == "__main__":
    seed_all()
    print(f"Seeded {len(SCHEMAS)} databases in {DATA_DIR}")
