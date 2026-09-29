from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, SessionUser
from app.services.blockchain import blockchain_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.get("/students", response_model=List[UserResponse])
def get_students(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all users with 'student' role"""
    students = db.query(User).filter(User.role == "student").all()
    return students

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate role
    valid_roles = ["admin", "teacher", "student"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    # Assign wallet address
    wallet_address = user_data.wallet_address
    if not wallet_address and blockchain_service.accounts:
        # Auto-assign from available Ganache accounts
        existing_wallets = [u.wallet_address for u in db.query(User).all()]
        available_accounts = [acc for acc in blockchain_service.accounts if acc not in existing_wallets]
        if available_accounts:
            wallet_address = available_accounts[0]

    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        wallet_address=wallet_address
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # If teacher, authorize on blockchain
    if db_user.role == "teacher" and wallet_address and blockchain_service.contract:
        try:
            admin_account = blockchain_service.accounts[0]
            blockchain_service.authorize_issuer(wallet_address, admin_account)
        except Exception as e:
            print(f"Warning: Could not authorize teacher on blockchain: {str(e)}")

    return db_user

@router.post("/login")
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and create session"""
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create session
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role

    return {
        "message": "Login successful",
        "user": UserResponse.from_orm(user)
    }

@router.post("/logout")
def logout(request: Request):
    """Logout user and clear session"""
    request.session.clear()
    return {"message": "Logout successful"}

@router.get("/me", response_model=SessionUser)
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """Get current logged-in user info"""
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return SessionUser(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        wallet_address=user.wallet_address
    )
