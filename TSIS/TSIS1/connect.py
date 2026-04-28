import psycopg2
import config

def get_connection():
    try:
        conn = psycopg2.connect(
            host=config.host,
            database=config.database,
            user=config.user,
            password=config.password
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
