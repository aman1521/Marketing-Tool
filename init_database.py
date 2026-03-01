#!/usr/bin/env python
"""
Database Initialization Script
Initializes PostgreSQL database and creates all tables from ORM models
Run this after PostgreSQL is running to set up the database
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.models.database import DatabaseConfig, verify_database_setup
from shared.models.orm_models import Base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database and create all tables"""
    
    logger.info("=" * 60)
    logger.info("Database Initialization Script")
    logger.info("=" * 60)
    
    # Verify database configuration
    logger.info("\n1. Verifying database configuration...")
    db_status = verify_database_setup()
    
    logger.info(f"   Database URL: {db_status['database_url']}")
    logger.info(f"   Pool Size: {db_status['pool_size']}")
    logger.info(f"   Max Overflow: {db_status['max_overflow']}")
    
    if not db_status['connection_successful']:
        logger.error("   ❌ Cannot connect to database. Make sure PostgreSQL is running.")
        logger.error(f"   Check your DATABASE_URL environment variable.")
        return False
    
    logger.info("   ✅ Database connection successful")
    
    # Create tables
    logger.info("\n2. Creating database tables...")
    try:
        DatabaseConfig.create_all_tables()
        logger.info("   ✅ All tables created successfully")
    except Exception as e:
        logger.error(f"   ❌ Error creating tables: {str(e)}")
        return False
    
    # Verify tables were created
    logger.info("\n3. Verifying tables...")
    db_status = verify_database_setup()
    
    if db_status['tables_created']:
        logger.info(f"   ✅ {db_status['tables_count']} tables created")
        logger.info("\n   Tables:")
        
        engine = DatabaseConfig.get_engine()
        inspector = __import__('sqlalchemy').inspect(engine)
        tables = inspector.get_table_names()
        
        for table in sorted(tables):
            logger.info(f"      - {table}")
    else:
        logger.warning("   ⚠️ No tables found after creation")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Database initialization complete!")
    logger.info("=" * 60)
    
    logger.info("\nNext steps:")
    logger.info("1. Start the services: docker-compose up -d")
    logger.info("2. Create a test user:")
    logger.info("   curl -X POST http://localhost:8001/api/v1/auth/register \\")
    logger.info("     -H 'Content-Type: application/json' \\")
    logger.info("     -d '{\"email\":\"test@example.com\",\"username\":\"testuser\",")
    logger.info("           \"password\":\"testpass\",\"first_name\":\"Test\",")
    logger.info("           \"last_name\":\"User\"}'")
    
    return True


def reset_database():
    """Reset database (WARNING: destructive)"""
    
    response = input(
        "\n⚠️  WARNING: This will drop all tables and delete all data!\n"
        "Are you sure you want to reset the database? (yes/no): "
    )
    
    if response.lower() != 'yes':
        logger.info("Reset cancelled.")
        return False
    
    logger.warning("Resetting database...")
    
    try:
        DatabaseConfig.drop_all_tables()
        logger.warning("✅ All tables dropped")
        
        # Recreate tables
        logger.info("Recreating tables...")
        DatabaseConfig.create_all_tables()
        logger.info("✅ Tables recreated")
        
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization tool")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset database (destructive operation)"
    )
    parser.add_argument(
        "--no-init",
        action="store_true",
        help="Skip initialization, only verify"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        success = reset_database()
    elif args.no_init:
        logger.info("Verifying database...")
        db_status = verify_database_setup()
        if db_status["connection_successful"]:
            logger.info(f"✅ Database connected. Tables: {db_status.get('tables_count', 0)}")
            success = True
        else:
            logger.error("❌ Database connection failed")
            success = False
    else:
        success = init_database()
    
    sys.exit(0 if success else 1)
