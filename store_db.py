import sqlite3

def create_or_reset_users_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute('DROP TABLE IF EXISTS images')

    c.execute('''
        CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_image(image_path, description):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO images (image_path, description) VALUES (?, ?)', (image_path, description))
    conn.commit()
    conn.close()

def fetch_all_images():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM images')
    images = c.fetchall()
    conn.close()
    return images
