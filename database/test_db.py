import psycopg2

# Replace these values with your PostgreSQL credentials
db_params = {
    'dbname': 'test_database',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': '5432'
}

def create_table():
    """Create a table if it doesn't exist"""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                chat_id VARCHAR(255), -- Adjust the size based on your needs
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                agreement BOOLEAN,
                subscription BOOLEAN,
                active BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

def insert_user(username, chat_id):
    """Insert a new user into the 'users' table"""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users2 (username, chat_id) VALUES (%s, %s)
    ''', (username, chat_id))

    conn.commit()
    conn.close()

def read_users():
    """Read all users from the 'users' table"""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users2')
    users = cursor.fetchall()

    conn.close()
    return users

def delete_user(user_id):
    """Delete a user from the 'users' table"""
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))

    conn.commit()
    conn.close()

# Uncomment the function calls you want to execute
create_table()
# insert_user('Fer','654321')
#
# # delete_user(6)
# print(read_users())