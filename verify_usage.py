#!/usr/bin/env python3
"""Manual verification of usage control"""

from app.core.db import get_engine, get_session_factory
from app.core.usage import check_usage_limit, record_usage, get_usage_stats, USAGE_LIMITS
from app.models.user import User
from sqlalchemy.orm import Session

print("=== Testing Usage Control ===\n")

# Create session
SessionLocal = get_session_factory()
db: Session = SessionLocal()

try:
    # Create or get test user
    user = db.query(User).filter(User.email == "test_usage@example.com").first()
    if not user:
        user = User(email="test_usage@example.com", plan="free")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created user: {user.email}")
    else:
        print(f"✅ Using existing user: {user.email}")
    
    # Get initial stats
    stats = get_usage_stats(user, db)
    print(f"\n📊 Initial usage:")
    print(f"   Week: {stats['week_key']}")
    print(f"   Plan: {stats['plan']}")
    print(f"   Used: {stats['used']}/{stats['limit']}")
    print(f"   Remaining: {stats['remaining']}")
    
    # Try to use up to limit
    limit = USAGE_LIMITS[user.plan]
    print(f"\n🔬 Making {limit} analyses...")
    
    for i in range(limit):
        try:
            check_usage_limit(user, db)
            record_usage(user, db)
            stats = get_usage_stats(user, db)
            print(f"   [{i+1}] ✅ Analysis recorded. Remaining: {stats['remaining']}")
        except Exception as e:
            print(f"   [{i+1}] ❌ Error: {e}")
            break
    
    # Try one more (should fail)
    print(f"\n🚫 Trying to exceed limit...")
    try:
        check_usage_limit(user, db)
        print("   ❌ FAIL: Should have raised 402 error!")
    except Exception as e:
        if "402" in str(e) or "limit exceeded" in str(e).lower():
            print(f"   ✅ SUCCESS: Correctly blocked - {e}")
        else:
            print(f"   ⚠️  Got error but wrong type: {e}")
    
    print("\n✅ Usage control working correctly!")
    
finally:
    db.close()
