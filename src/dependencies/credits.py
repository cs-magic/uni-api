from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.security import get_current_user
from src.database import get_db
from src.models.user import User
from src.schemas.user import CreditsCheck


async def verify_credits(
    credits_check: CreditsCheck, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.credits < credits_check.required_credits:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits")
    return True
