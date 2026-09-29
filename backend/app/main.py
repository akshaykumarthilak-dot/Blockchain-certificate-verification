from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.database import engine, Base, SessionLocal
from app.routers import auth, certificates, admin
from app.services.blockchain import blockchain_service
from app.models.user import User
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Certificate Verification System",
    description="Blockchain-based certificate authentication and verification system",
    version="1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-change-this-in-production-please",
    max_age=3600
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(certificates.router)
app.include_router(admin.router)


def reassign_wallets():
    if not blockchain_service.w3 or not blockchain_service.w3.is_connected():
        print("Skipping wallet reassignment: Ganache not connected")
        return

    ganache_accounts = list(blockchain_service.w3.eth.accounts)
    if not ganache_accounts:
        print("Skipping wallet reassignment: No Ganache accounts found")
        return

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id).all()

        # Separate users into those with valid and invalid wallets
        valid_users = []
        invalid_users = []
        for user in users:
            if user.wallet_address in ganache_accounts:
                valid_users.append(user)
            else:
                invalid_users.append(user)

        # Find accounts not yet assigned to any valid user
        used_accounts = set(u.wallet_address for u in valid_users)
        free_accounts = [a for a in ganache_accounts if a not in used_accounts]

        print(f"Valid wallet users: {len(valid_users)}, Need reassignment: {len(invalid_users)}, Free accounts: {len(free_accounts)}")

        for user in invalid_users:
            if not free_accounts:
                print(f"Warning: No free Ganache account for {user.email}. Keeping old wallet.")
                continue
            new_wallet = free_accounts.pop(0)
            print(f"Updating wallet for {user.email} ({user.role}): {user.wallet_address} -> {new_wallet}")
            user.wallet_address = new_wallet

        db.commit()
        print("Wallet reassignment complete.")

        # Re-authorize all teachers on blockchain
        admin_account = ganache_accounts[0]
        for user in users:
            if user.role == "teacher" and user.wallet_address and blockchain_service.contract:
                try:
                    blockchain_service.authorize_issuer(user.wallet_address, admin_account)
                    print(f"Re-authorized teacher {user.email} on blockchain")
                except Exception as e:
                    print(f"Could not re-authorize {user.email}: {str(e)}")

    except Exception as e:
        print(f"Error during wallet reassignment: {str(e)}")
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    print("Starting Certificate Verification System...")

    contract_path = os.path.join(
        os.path.dirname(__file__),
        "../../blockchain/build/contracts/CertificateAuthentication.json"
    )

    if os.path.exists(contract_path):
        blockchain_service.load_contract(contract_path)
    else:
        print("Warning: Smart contract not found. Please deploy the contract first.")
        print(f"Expected path: {contract_path}")

    reassign_wallets()


@app.get("/")
def root():
    return {
        "message": "Certificate Verification System API",
        "version": "1.0.0",
        "blockchain_connected": blockchain_service.w3.is_connected() if blockchain_service.w3 else False,
        "contract_loaded": blockchain_service.contract is not None
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "blockchain_connected": blockchain_service.w3.is_connected() if blockchain_service.w3 else False,
        "contract_loaded": blockchain_service.contract is not None,
        "contract_address": blockchain_service.contract_address
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)