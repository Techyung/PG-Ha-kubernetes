import psycopg2
from psycopg2 import sql
from faker import Faker
import random

# Initialize Faker instance
fake = Faker()

# PostgreSQL connection details
HOST = "localhost"  # Change this if you are connecting through an external IP or service name
PORT = '5433'  # The port you are forwarding to locally
USER = 'postgres'  # The PostgreSQL username
PASSWORD = 'GTBG1sznSr'  # The PostgreSQL password (replace with actual password)
DATABASE = 'library'  # The database name to be created if not exists

# Function to connect to PostgreSQL (default database to connect to template1 or postgres)
def connect_to_postgres(database='postgres'):
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        dbname=database
    )
    return conn

# Function to create the database if it doesn't exist
def create_database():
    conn = connect_to_postgres('postgres')  # Connect to the default database (template1 or postgres)
    cur = conn.cursor()

    # Switch autocommit mode for CREATE DATABASE
    conn.autocommit = True

    # Check if the database exists and create it if not
    try:
        cur.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [DATABASE])
        exists = cur.fetchone()
        if not exists:
            print(f"Database '{DATABASE}' does not exist. Creating it now...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DATABASE)))
            print(f"Database '{DATABASE}' created successfully.")
        else:
            print(f"Database '{DATABASE}' already exists.")
    except Exception as e:
        print(f"Error while checking/creating database: {e}")
    finally:
        cur.close()
        conn.close()

# Function to create tables (Author and Book)
def create_tables():
    conn = connect_to_postgres(DATABASE)  # Connect to the newly created database
    cur = conn.cursor()
    
    # Create Author table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL
    );
    """)

    # Create Book table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        genre VARCHAR(100),
        author_id INTEGER REFERENCES authors(id)
    );
    """)

    conn.commit()
    print("Tables created successfully!")

# Function to insert random data
def insert_data(num_records=100000):
    authors = set()  # To ensure unique authors (we will limit to 10,000 unique authors)
    conn = connect_to_postgres(DATABASE)  # Connect to the database where data is being inserted
    cur = conn.cursor()

    for _ in range(num_records):
        # Generate random author if needed
        if len(authors) < num_records // 10:  # Aim for 10% authors
            name = fake.name()
            email = fake.email()
            cur.execute("""
            INSERT INTO authors (name, email) VALUES (%s, %s) RETURNING id;
            """, (name, email))
            author_id = cur.fetchone()[0]
            authors.add(author_id)

        # Pick a random author
        author_id = random.choice(list(authors))
        
        # Generate random book
        title = fake.sentence(nb_words=4)
        genre = fake.word()
        
        cur.execute("""
        INSERT INTO books (title, genre, author_id) VALUES (%s, %s, %s);
        """, (title, genre, author_id))

    conn.commit()
    print(f"Inserted {num_records} records into 'authors' and 'books'.")

    cur.close()
    conn.close()

# Run the script
try:
    create_database()  # Ensure the database exists
    create_tables()    # Create tables if they don't exist
    insert_data(100000)  # Insert 100,000 records
finally:
    print("Database population complete.")
