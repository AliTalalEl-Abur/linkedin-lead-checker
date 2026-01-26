"""
Simple migration script to create the feedback table
Run this file to update your database with the feedback table
"""
import sqlite3
from pathlib import Path

def migrate():
    """Create feedback table in the database"""
    db_path = Path(__file__).parent.parent / "linkedin_lead_checker.db"
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='feedback'
        """)
        
        if cursor.fetchone():
            print("✓ Feedback table already exists")
            return
        
        # Create feedback table
        cursor.execute("""
            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email VARCHAR(255),
                message TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'new' NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_feedback_id ON feedback (id)")
        cursor.execute("CREATE INDEX ix_feedback_user_id ON feedback (user_id)")
        
        conn.commit()
        print("✓ Feedback table created successfully")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
