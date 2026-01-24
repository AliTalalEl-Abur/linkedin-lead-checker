"""
Migration script to add month_key column to usage_events table.
This supports the transition from weekly to monthly usage limits.

Run manually with: python migrations/add_month_key_to_usage_events.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import get_settings
from app.core.utils import get_month_key_for_date


def migrate():
    """Add month_key column and populate from existing week_key dates."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Check if column exists (PostgreSQL compatible)
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'usage_events'
        """))
        columns = [row[0] for row in result]
        
        if 'month_key' in columns:
            print("✅ month_key column already exists")
            return
        
        print("Adding month_key column...")
        
        # Add column (nullable for now)
        conn.execute(text("ALTER TABLE usage_events ADD COLUMN month_key VARCHAR(16)"))
        conn.commit()
        
        print("✅ Column added")
        
        # Populate month_key from created_at for existing records
        print("Populating month_key for existing records...")
        result = conn.execute(text("SELECT id, created_at FROM usage_events WHERE month_key IS NULL"))
        rows = result.fetchall()
        
        for row_id, created_at in rows:
            if created_at:
                # Parse datetime string
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    dt = created_at
                
                month_key = get_month_key_for_date(dt)
                conn.execute(
                    text("UPDATE usage_events SET month_key = :month_key WHERE id = :id"),
                    {"month_key": month_key, "id": row_id}
                )
        
        conn.commit()
        print(f"✅ Updated {len(rows)} existing records")
        
        # Create index on month_key
        print("Creating index on month_key...")
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_usage_events_month_key ON usage_events(month_key)"))
        conn.commit()
        print("✅ Index created")
        
        print("\n✅ Migration complete!")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
