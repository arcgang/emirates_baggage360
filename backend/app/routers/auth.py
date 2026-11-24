"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..schemas.auth_schemas import PrincipalContext
from ..models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    """Login credentials."""
    email: str
    password: str


class LoginResponse(BaseModel):
    """Login response with token and user info."""
    access_token: str
    token_type: str
    user: PrincipalContext


@router.post("/auth/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.
    
    For this initial scaffold, performs basic email lookup only.
    Password verification and JWT token generation will be implemented in subsequent tasks
    when the User model includes hashed_password field.
    """
    # Look up user by external_subject (email)
    user = db.query(User).filter(User.external_subject == credentials.email).first()
    
    if not user or not user.active_flag:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # For this scaffold, accept the demo password Demo1234! for seed users
    # Production implementation will verify hashed passwords
    if credentials.password != "Demo1234!":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # For demo purposes, generate a simple token (user_id)
    # Production implementation will use proper JWT signing with exp claim
    token = f"demo_token_{user.id}"
    
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=PrincipalContext(
            user_id=user.id,
            role=user.role_code,
            display_name=user.display_name,
            scopes=[f"{user.role_code}:read", f"{user.role_code}:write"],
        )
    )


@router.post("/auth/logout")
def logout():
    """
    Logout current session.
    
    For this initial scaffold, returns success.
    Full session revocation will be implemented in subsequent tasks.
    """
    return {"status": "logged_out"}


@router.get("/auth/me", response_model=PrincipalContext)
def get_current_principal(db: Session = Depends(get_db)):
    """Get current authenticated principal context.
    
    For this initial scaffold, returns a stub response.
    Full authentication will be implemented in subsequent tasks.
    """
    return PrincipalContext(
        user_id="00000000-0000-0000-0000-000000000001",
        role="operations",
        display_name="Mariam Al Suwaidi",
        scopes=["operations:read", "operations:write"],
    )
