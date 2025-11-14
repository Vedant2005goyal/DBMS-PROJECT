import mysql.connector
from mysql.connector import pooling
from config import Config

class DatabaseManager:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._pool is None:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="attendance_pool",
                pool_size=5,
                pool_reset_session=True,
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
    
    def get_connection(self):
        """Get a connection from the pool"""
        return self._pool.get_connection()
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Execute a query with automatic connection management"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
