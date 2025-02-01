import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    user="jialihuang",
    password="yourpassword",  # Ensure this is correct
    dbname="my_local_db"
)

cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

# Create tasks table
cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task TEXT NOT NULL
);
""")

# Create quotes table
cur.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    quote TEXT NOT NULL,
    emoji TEXT
);
""")

# Insert predefined motivational quotes if the table is empty
cur.execute("SELECT COUNT(*) FROM quotes;")
count = cur.fetchone()[0]

if count == 0:
    cur.execute("""
    INSERT INTO quotes (quote, emoji) VALUES
    ('Believe in yourself!', '💪'),
    ('Keep pushing forward.', '🚀'),
    ('Success is no accident.', '🎯'),
    ('Stay positive and work hard.', '😊');
    """)

conn.commit()
cur.close()
conn.close()
