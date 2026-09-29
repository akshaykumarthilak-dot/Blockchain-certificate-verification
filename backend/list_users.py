from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./certificate_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_users():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id, username, email, role, wallet_address FROM users"))
        print(f"{'ID':<5} {'Username':<15} {'Role':<10} {'Wallet Address'}")
        print("-" * 80)
        for row in result:
            print(f"{row[0]:<5} {row[1]:<15} {row[3]:<10} {row[4]}")
    except Exception as e:
        print(f"Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
