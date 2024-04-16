import psycopg2
import os
from shared.models import UserData

# TODO: Use environment variables to store the database credentials


def generate_where_clause(filter_items: dict) -> str:
    """Generate the WHERE clause based on the provided filters"""
    conditions = []
    for key, value in filter_items.items():
        conditions.append(f"{key} = %s")

    if conditions:
        return "WHERE " + " AND ".join(conditions)
    else:
        return ""


class DatabaseConnector:
    def __init__(self, db_name, user, password, host, port):
        self.db_params = {
            'dbname': db_name,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.conn = psycopg2.connect(**self.db_params)
        self.cursor = self.conn.cursor()

    def _close(self):
        self.conn.close()

    def _commit_and_close(self):
        self.conn.commit()
        self._close()

    def table_exists(self):
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{self.db_params['dbname']}')"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]

    def create_table(self):
        """Create a table if it doesn't exist"""

        self.conn = psycopg2.connect(**self.db_params)
        self.cursor = self.conn.cursor()

        self.cursor.execute('''
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

    def insert_user(self, user: UserData):
        """Insert a new user into the 'users' table"""
        try:
            if not self.table_exists():
                self.create_table()
            self.cursor.execute(user.get_query_string())

        except Exception as e:
            raise ValueError(f"This is the error! {e}")

    def read_users(self, **kwargs):
        try:
            where_clause = generate_where_clause(kwargs)
            query = f"SELECT * FROM users {where_clause}"
            self.cursor.execute(query, tuple(kwargs.values()))
            users = self.cursor.fetchall()

            user_objects = [UserData.from_database(user) for user in users]
            return user_objects

            # for user_object in user_objects:
            #     print(user_object)

        except Exception as e:
            raise ValueError(f"This is the error! {e}")

    def delete_user(self, chat_id):
        try:
            query = '''
                DELETE FROM users
                WHERE chat_id = %s
            '''
            self.cursor.execute(query, (chat_id,))
            self._commit_and_close()

        except Exception as e:
            raise ValueError(f"This is the error! {e}")

    def update_user(self, chat_id, **kwargs):
        try:
            set_clause = ", ".join(f"{key} = %s" for key in kwargs)
            query = f'''
                UPDATE users
                SET {set_clause}
                WHERE chat_id = %s
            '''

            values = tuple(kwargs.values()) + (chat_id,)
            self.cursor.execute(query, values)
            self._commit_and_close()

        except Exception as e:
            raise ValueError(f"This is the error! {e}")

    def user_exists(self, chat_id):
        """Check if a user exists in the 'users' table by chat_id"""
        try:
            if not self.table_exists():
                self.create_table()

            query = '''
                SELECT EXISTS (
                    SELECT 1 FROM users
                    WHERE chat_id = %s
                )
            '''
            self.cursor.execute(query, (chat_id,))
            return self.cursor.fetchone()[0]

        except Exception as e:
            raise ValueError(f"This is the error! {e}")


#
db_connector_testing = DatabaseConnector(
    db_name=os.environ.get('DB_NAME', None),
    user=os.environ.get('DB_USER', None),
    password=os.environ.get('DB_PASSWORD', None),
    host=os.environ.get('DB_HOST', 'localhost'),
    port=os.environ.get('DB_PORT', '5432'),
)

# Test to modify user information Use chat_id and then just items to modify db_connector_testing.update_user(
# chat_id='0123456789', latitude=99.000000, longitude=00.999999, agreement=True, subscription=True, active=True)
# db_connector_testing.update_user(chat_id='0123456789', agreement=False, subscription=False, active=False)

# Test to delete user, use only chat_id
# db_connector_testing.delete_user('9876543210')

# Test users print, you can use an empty dic or put the filters inside
filters = {}
# filters = {'active': False, 'subscription': False, 'chat_id': '0123456789'}
db_connector_testing.read_users(**filters)

# Test for checking if user already exists
# if db_connector_testing.user_exists('0123456789'):
#     print("User already exists")
# else:
#     print("User does not exist")
