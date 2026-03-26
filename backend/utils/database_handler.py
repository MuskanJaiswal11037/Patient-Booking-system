"""
Database Handler for Hospital Management System.

Uses psycopg2 for synchronous PostgreSQL connections with connection pooling.
Connection URL format: postgresql://username:password@host:port/database_name
Connection is created once in __init__ and reused for all queries.
Uses atexit to automatically close the connection on program exit.
"""

import logging
import atexit
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Optional, Dict, List
from backend.config import settings

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    """Base database exception."""
    pass


class DatabaseHandler:
    """Synchronous database handler using psycopg2 with connection pooling."""
    
    def __init__(self, database_url: str):
        """
        Initialize DatabaseHandler with persistent connection.
        
        Parameters
        ----------
        database_url : str
            PostgreSQL connection URL (postgresql://user:password@host:port/db)
        
        Raises
        ------
        ValueError
            If database_url is empty
        DatabaseException
            If connection to database fails
        """
        if not database_url:
            raise ValueError("Database URL cannot be empty")
        
        self.database_url = database_url
        self.conn = None
        
        # Create persistent connection
        self._connect()
        
        # Register cleanup function to close connection on exit
        atexit.register(self._close)
    
    def _connect(self) -> None:
        """
        Establish database connection.
        """
        try:
            self.conn = psycopg2.connect(self.database_url)
            logger.info("✓ Database connection established")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            self.conn = None
            raise DatabaseException(f"Connection failed: {str(e)}")
        
    def get_connection(self):
        """
        Get the current database connection.
        
        Returns
        -------
        psycopg2.extensions.connection
            Active database connection
        
        Raises
        ------
        DatabaseException
            If connection is not established
        """
        if not self.conn:
            raise DatabaseException("Database connection is not established")
        return self.conn
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Execute SQL query using persistent connection.
        
        Parameters
        ----------
        query : str
            SQL query to execute (SELECT only)
        params : Optional[Dict[str, Any]]
            Optional query parameters
        
        Returns
        -------
        List[Any]
            Query results as list of dictionaries
        
        Raises
        ------
        DatabaseException
            If query execution fails
        """
        if not self.conn:
            raise DatabaseException("Database connection is not initialized")
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                self.conn.commit()
                if cursor.description:
                    result = cursor.fetchall()
                else:       
                    result = []
                
                return result
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {str(e)}")
            self.conn.rollback()
            raise DatabaseException(f"Query failed: {str(e)}")
    
    def _close(self) -> None:
        """
        Close the database connection.
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("✓ Database connection closed")
            except psycopg2.Error as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.conn = None

db_handler = DatabaseHandler(settings.DATABASE_URL)