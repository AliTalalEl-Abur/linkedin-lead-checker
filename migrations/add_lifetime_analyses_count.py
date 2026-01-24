"""
Migration script to add lifetime_analyses_count column to users table.
This tracks FREE plan usage (lifetime limit of 3 analyses).

Run manually with: python migrations/add_lifetime_analyses_count.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


def migrate():
    """Add lifetime_analyses_count column to users table."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if column exists (PostgreSQL compatible)
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """))
        columns = [row[0] for row in result]
        
        if 'lifetime_analyses_count' in columns:
            print("✅ lifetime_analyses_count column already exists")
            return
        
        print("Adding lifetime_analyses_count column...")
        
        # Add column with default value 0
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN lifetime_analyses_count INTEGER DEFAULT 0 NOT NULL
        """))
        conn.commit()
        
        print("✅ Column added with default value 0")
        
        print("\n✅ Migration complete!")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
