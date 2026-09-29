from web3 import Web3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
if not w3.is_connected():
    print("❌ Failed to connect to Ganache")
    exit(1)

accounts = w3.eth.accounts
print(f"✅ Connected to Ganache. Found {len(accounts)} accounts.")

# Database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./certificate_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_wallets():
    db = SessionLocal()
    try:
        # Update Teacher
        if len(accounts) > 0:
            teacher_addr = accounts[0]
            db.execute(text("UPDATE users SET wallet_address = :addr WHERE username = 'teacher@mail.com'"), {"addr": teacher_addr})
            print(f"Updated teacher@mail.com -> {teacher_addr}")

        # Update Student
        if len(accounts) > 1:
            student_addr = accounts[1]
            db.execute(text("UPDATE users SET wallet_address = :addr WHERE username = 'student@mail.com'"), {"addr": student_addr})
            print(f"Updated student@mail.com -> {student_addr}")

        # Update Admin
        if len(accounts) > 2:
            admin_addr = accounts[2]
            db.execute(text("UPDATE users SET wallet_address = :addr WHERE username = 'admin@mail.com'"), {"addr": admin_addr})
            print(f"Updated admin@mail.com -> {admin_addr}")

        db.commit()
        print("✅ Wallet addresses updated successfully.")
        
    except Exception as e:
        print(f"❌ Error updating wallets: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_wallets()
