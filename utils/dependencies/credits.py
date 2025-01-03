from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.security import get_current_user
from utils.database import get_db
from models.user import User
from schema.user import CreditsCheck


async def verify_credits(
    credits_check: CreditsCheck, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if current_user.credits < credits_check.required_credits:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits")
    return True
