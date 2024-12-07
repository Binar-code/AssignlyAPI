import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login STRING NOT NULL UNIQUE,
    tag STRING NOT NULL UNIQUE,
    password STRING NOT NULL,
    profile_image STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Group table
cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name STRING NOT NULL UNIQUE,
    description STRING NOT NULL,
    image STRING,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Merge table users to group
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_to_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (group_id) REFERENCES groups (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Task table
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER REFERENCES groups (id) ON DELETE CASCADE,
    owner_id INTEGER REFERENCES users (id) ON DELETE CASCADE,
    name STRING NOT NULL UNIQUE,
    summary STRING NOT NULL,       
    description STRING NOT NULL,
    deadline DATETIME NOT NULL,
    status INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Merge table task to user
cursor.execute('''
CREATE TABLE IF NOT EXISTS task_to_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (task_id) REFERENCES tasks (id)
)
''')

connection.commit()
connection.close()
