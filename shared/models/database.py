"""
Database Configuration and Session Management
Handles PostgreSQL connection, pooling, and session management
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

# Database Configuration from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://aios_user:aios_password@localhost:5432/aios_database"
)

POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 20))
MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 10))
POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", 3600))
ECHO_SQL = os.getenv("DATABASE_ECHO_SQL", "False").lower() == "true"


class DatabaseConfig:
    """Database configuration and engine initialization"""
    
    _engine = None
    _session_local = None
    
    @classmethod
    def get_engine(cls):
        """Get or create database engine"""
        if cls._engine is None:
            logger.info(f"Initializing database engine: {DATABASE_URL}")
            
            cls._engine = create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_recycle=POOL_RECYCLE,
                echo=ECHO_SQL,
                connect_args={
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000"
                }
            )
            
            # Add connection pool event listeners
            @event.listens_for(cls._engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                logger.debug("Database connection established")
            
            @event.listens_for(cls._engine, "close")
            def receive_close(dbapi_conn, connection_record):
                logger.debug("Database connection closed")
            
            @event.listens_for(cls._engine, "detach")
            def receive_detach(dbapi_conn, connection_record):
                logger.debug("Database connection detached")
        
        return cls._engine
    
    @classmethod
    def get_session_factory(cls):
        """Get or create session factory"""
        if cls._session_local is None:
            engine = cls.get_engine()
            cls._session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
            logger.info("Session factory initialized")
        
        return cls._session_local
    
    @classmethod
    def get_session(cls) -> Session:
        """Create new database session"""
        session_factory = cls.get_session_factory()
        return session_factory()
    
    @classmethod
    def create_all_tables(cls):
        """Create all tables from ORM models"""
        from shared.models.orm_models import Base
        
        engine = cls.get_engine()
        logger.info("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("All tables created successfully")
    
    @classmethod
    def drop_all_tables(cls):
        """Drop all tables (WARNING: destructive)"""
        from shared.models.orm_models import Base
        
        engine = cls.get_engine()
        logger.warning("Dropping all tables!")
        Base.metadata.drop_all(bind=engine)
        logger.warning("All tables dropped")
    
    @classmethod
    def test_connection(cls) -> bool:
        """Test database connection"""
        try:
            engine = cls.get_engine()
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            return False
    
    @classmethod
    def close(cls):
        """Close database engine"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            logger.info("Database engine closed")


# Dependency for FastAPI
def get_db() -> Session:
    """FastAPI dependency to inject database session"""
    session = DatabaseConfig.get_session()
    try:
        yield session
    finally:
        session.close()


# Helper function to verify database setup
def verify_database_setup() -> dict:
    """Verify database is properly configured and connected"""
    status = {
        "database_url": DATABASE_URL[:30] + "***" if len(DATABASE_URL) > 30 else DATABASE_URL,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "connection_successful": DatabaseConfig.test_connection(),
        "tables_created": False
    }
    
    if status["connection_successful"]:
        try:
            from shared.models.orm_models import Base
            engine = DatabaseConfig.get_engine()
            # Check if tables exist
            inspector = __import__('sqlalchemy').inspect(engine)
            tables = inspector.get_table_names()
            status["tables_created"] = len(tables) > 0
            status["tables_count"] = len(tables)
        except Exception as e:
            logger.error(f"Error verifying tables: {str(e)}")
    
    return status


if __name__ == "__main__":
    # Test database connection when run directly
    logging.basicConfig(level=logging.INFO)
    
    print("Testing database configuration...")
    status = verify_database_setup()
    
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if status["connection_successful"]:
        print("\n✅ Database is properly configured and connected!")
    else:
        print("\n❌ Database connection failed. Check your configuration.")
