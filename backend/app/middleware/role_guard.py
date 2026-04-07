"""
Role-based access guard.
Usage:
  @router.post("/admin-only")
  def admin_route(user: User = Depends(require_role("ADMIN"))):
      ...
"""

from fastapi import Depends, HTTPException, status

from app.db.models import User
from app.middleware.auth import get_current_user


def require_role(*allowed_roles: str):
    """
    Returns a FastAPI dependency that raises 403 if the
    authenticated user's role is not in allowed_roles.
    """

    def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not permitted. Required: {list(allowed_roles)}",
            )
        return current_user

    return _guard
