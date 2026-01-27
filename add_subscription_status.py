"""
Add subscription_status column to users table (PostgreSQL)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.db import get_engine

def add_subscription_status_column():
    """Add subscription_status column if it doesn't exist"""
    engine = get_engine()
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='subscription_status';
        """))
        
        if result.fetchone() is None:
            print("Adding subscription_status column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN subscription_status VARCHAR(50);
            """))
            conn.commit()
            print("✅ Column added successfully")
        else:
            print("✅ Column subscription_status already exists")
        
        # Check monthly_analyses_count
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='monthly_analyses_count';
        """))
        
        if result.fetchone() is None:
            print("Adding monthly_analyses_count column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN monthly_analyses_count INTEGER NOT NULL DEFAULT 0;
            """))
            conn.commit()
            print("✅ Column added successfully")
        else:
            print("✅ Column monthly_analyses_count already exists")
        
        # Check monthly_analyses_reset_at
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='monthly_analyses_reset_at';
        """))
        
        if result.fetchone() is None:
            print("Adding monthly_analyses_reset_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN monthly_analyses_reset_at TIMESTAMP WITH TIME ZONE;
            """))
            conn.commit()
            print("✅ Column added successfully")
        else:
            print("✅ Column monthly_analyses_reset_at already exists")

if __name__ == "__main__":
    try:
        add_subscription_status_column()
        print("\n✅ Migration completed successfully")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
