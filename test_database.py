#!/usr/bin/env python
"""
Test Database Setup
Quick script to verify database connectivity and operations
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.models.database import DatabaseConfig, verify_database_setup
from shared.models.orm_models import User
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test basic database connection"""
    logger.info("\n" + "=" * 60)
    logger.info("1. Testing Database Connection")
    logger.info("=" * 60)
    
    if DatabaseConfig.test_connection():
        logger.info("✅ Database connection test passed")
        return True
    else:
        logger.error("❌ Database connection test failed")
        return False


def test_database_status():
    """Verify database setup status"""
    logger.info("\n" + "=" * 60)
    logger.info("2. Checking Database Status")
    logger.info("=" * 60)
    
    status = verify_database_setup()
    
    logger.info(f"   Connection URL: {status['database_url']}")
    logger.info(f"   Pool Size: {status['pool_size']}")
    logger.info(f"   Connected: {status['connection_successful']}")
    logger.info(f"   Tables Created: {status['tables_created']}")
    if 'tables_count' in status:
        logger.info(f"   Tables Count: {status['tables_count']}")
    
    if status['connection_successful'] and status['tables_created']:
        logger.info("✅ Database is properly initialized")
        return True
    elif status['connection_successful']:
        logger.warning("⚠️ Database is connected but tables not created")
        logger.warning("   Run: python init_database.py")
        return False
    else:
        logger.error("❌ Database is not connected")
        return False


def test_create_user():
    """Test creating a user"""
    logger.info("\n" + "=" * 60)
    logger.info("3. Testing User Creation")
    logger.info("=" * 60)
    
    try:
        session = DatabaseConfig.get_session()
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            password_hash="$2b$12$test_hash",  # This is a test hash
            first_name="Test",
            last_name="User",
            role="business_owner",
            is_active=True
        )
        
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        logger.info(f"   Created user: {test_user.email}")
        logger.info(f"   User ID: {test_user.id}")
        logger.info("✅ User creation test passed")
        
        # Clean up
        session.delete(test_user)
        session.commit()
        session.close()
        
        return True
    
    except Exception as e:
        logger.error(f"❌ User creation test failed: {str(e)}")
        session.rollback()
        session.close()
        return False


def test_query_users():
    """Test querying users"""
    logger.info("\n" + "=" * 60)
    logger.info("4. Testing User Query")
    logger.info("=" * 60)
    
    try:
        session = DatabaseConfig.get_session()
        
        # Query all users
        users = session.query(User).all()
        
        logger.info(f"   Total users in database: {len(users)}")
        
        if users:
            for user in users[:5]:  # Show first 5
                logger.info(f"      - {user.email} ({user.role})")
        
        session.close()
        logger.info("✅ User query test passed")
        return True
    
    except Exception as e:
        logger.error(f"❌ User query test failed: {str(e)}")
        session.close()
        return False


def test_all():
    """Run all tests"""
    logger.info("\n" + "╔" + "=" * 58 + "╗")
    logger.info("║  Database Setup Verification Tests                     ║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = {
        "Connection Test": test_database_connection(),
        "Status Check": test_database_status(),
        "User Creation": test_create_user(),
        "User Query": test_query_users(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✅ All tests passed! Database is ready to use.")
        return True
    else:
        logger.warning(f"\n⚠️ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
