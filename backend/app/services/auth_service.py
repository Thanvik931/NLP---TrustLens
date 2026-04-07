"""
Auth business logic — register and login.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.schemas.auth import RegisterRequest, TokenResponse, UserOut


VALID_ROLES = {"ADMIN", "AUDITOR", "VIEWER"}


def register_user(payload: RegisterRequest, db: Session) -> TokenResponse:
    """
    Create a new user. Returns a JWT token immediately (auto-login).
    """
    # Validate role
    role = payload.role.upper()
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{payload.role}'. Must be one of {list(VALID_ROLES)}",
        )

    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already registered",
        )

    # Create user
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=str(user.id), role=user.role)
    return _build_token_response(token, user)


def login_user(email: str, password: str, db: Session) -> TokenResponse:
    """
    Verify credentials. Returns a JWT token on success.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=str(user.id), role=user.role)
    return _build_token_response(token, user)


def _build_token_response(token: str, user: User) -> TokenResponse:
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserOut(
            id=str(user.id),
            email=user.email,
            role=user.role,
            created_at=user.created_at.isoformat(),
        ),
    )
