from app.core.db import get_engine, Base, get_session_factory
from app.models.user import User
from app.core.security import create_access_token

# Test DB connection
print("Testing DB...")
engine = get_engine()
Base.metadata.create_all(bind=engine)
print("✅ DB OK")

# Test user creation
print("\nTesting user creation...")
SessionLocal = get_session_factory()
db = SessionLocal()
try:
    # Check if user exists
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(email="test@example.com", plan="free")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ User created: {user.id}, {user.email}")
    else:
        print(f"✅ User exists: {user.id}, {user.email}")
    
    # Test token creation
    print("\nTesting token creation...")
    token = create_access_token(data={"sub": user.id, "email": user.email})
    print(f"✅ Token created: {token[:50]}...")
    
finally:
    db.close()

print("\n✅ All manual tests passed!")
