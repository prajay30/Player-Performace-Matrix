import sqlite3

DATABASE = "fplayerpm.db"

def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create players table with a photo column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            club TEXT,
            nationality TEXT,
            appearances INTEGER,
            goals INTEGER,
            assists INTEGER,
            photo TEXT NOT NULL
        )
    ''')

    # Insert sample data with player photos
    sample_players = [
        ("Lionel Messi", "Forward", "Inter Miami", "Argentina", 1000, 800, 350, "messi.jpg"),
        ("Cristiano Ronaldo", "Forward", "Al Nassr", "Portugal", 1100, 850, 250, "ronaldo.jpg"),
        ("Kevin De Bruyne", "Midfielder", "Manchester City", "Belgium", 500, 120, 250, "debruyne.jpg"),
        ("Kylian Mbappé", "Forward", "Paris Saint-Germain", "France", 400, 200, 100, "mbappe.jpg"),
        ("Neymar Jr", "Forward", "Al Hilal", "Brazil", 500, 230, 180, "neymar.jpg")
    ]

    cursor.executemany('''
        INSERT INTO players (name, position, club, nationality, appearances, goals, assists, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_players)

    conn.commit()
    conn.close()
    print("Database setup complete with player photos! ✅")

if __name__ == "__main__":
    create_database()
