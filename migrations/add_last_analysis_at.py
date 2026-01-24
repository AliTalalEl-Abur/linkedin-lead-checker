"""
Migration script to add last_analysis_at column to users table.
This tracks when the user last ran an analysis (for rate limiting).

Run manually with: python migrations/add_last_analysis_at.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings


def migrate():
    """Add last_analysis_at column to users table."""
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
        
        if 'last_analysis_at' in columns:
            print("✅ last_analysis_at column already exists")
            return
        
        print("Adding last_analysis_at column...")
        
        # Add column (nullable, NULL by default)
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN last_analysis_at TIMESTAMP WITH TIME ZONE
        """))
        conn.commit()
        
        print("✅ Column added")
        
        print("\n✅ Migration complete!")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
