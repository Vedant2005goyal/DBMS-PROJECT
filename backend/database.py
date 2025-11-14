import mysql.connector
from mysql.connector import pooling
from config import Config

class DatabaseManager:
    _instance = None
    _pool = None  # CHANGED: This will hold the pool for the class
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # CHANGED: We now check the *class* variable.
        # This __init__ will run every time, but the 'if'
        # will only pass on the very first instantiation.
        if DatabaseManager._pool is None:
            DatabaseManager._pool = pooling.MySQLConnectionPool(
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
        # CHANGED: Get the pool from the class, not the instance
        if DatabaseManager._pool is None:
            raise RuntimeError("Database pool not initialized")
        return DatabaseManager._pool.get_connection()
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Execute a query with automatic connection management"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute(query, params or ())
            
            # Determine if this is a read-only query
            query_upper = query.strip().upper()
            is_read_only = query_upper.startswith('SELECT') or query_upper.startswith('SHOW')
            
            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch:
                result = cursor.fetchall()
            
            # CHANGED: Major logic fix
            if is_read_only:
                # This is a SELECT query, no commit needed.
                pass
            else:
                # This is an INSERT, UPDATE, DELETE, etc.
                # It MUST be committed.
                conn.commit()
                if not fetch and not fetch_one:
                    # If it was a simple INSERT/UPDATE, return lastrowid
                    result = cursor.lastrowid
                # If 'fetch' was true (e.g., for RETURNING), 
                # 'result' already has the fetched data.
            
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()