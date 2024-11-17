from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
import stripe

from settings import settings
from auth.oauth import OAuthHandler
from auth.security import get_password_hash, verify_password, create_access_token, get_current_user
from database.utils import get_db
from dependencies.credits import verify_credits
from database.models.user import Transaction, User
from schemas.user import UserResponse, UserCreate, Token, CreditsCheck

account_router = APIRouter(prefix='/account', tags=['Account'])

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@account_router.post('/register', response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) |
        (User.email == user_data.email) |
        (User.phone == user_data.phone)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email/phone already registered"
        )
    
    # Create new user
    db_user = User(
        **user_data.dict(exclude={'password'}),
        hashed_password=get_password_hash(user_data.password) if user_data.password else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@account_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")

@account_router.post("/deposit")
async def create_deposit(
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Create Stripe payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="usd",
            metadata={"user_id": current_user.id}
        )
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            type="deposit",
            stripe_payment_id=payment_intent.id,
            status="pending"
        )
        db.add(transaction)
        db.commit()
        
        return {"client_secret": payment_intent.client_secret}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@account_router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            user_id = payment_intent.metadata.get("user_id")
            amount = payment_intent.amount / 100  # Convert from cents
            
            # Update transaction and user credits
            transaction = db.query(Transaction).filter(
                Transaction.stripe_payment_id == payment_intent.id
            ).first()
            
            if transaction:
                transaction.status = "completed"
                user = db.query(User).filter(User.id == user_id).first()
                user.credits += amount
                db.commit()
                
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@account_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Example of using credits verification
@account_router.post("/consume-credits")
async def consume_credits(
    credits_check: CreditsCheck,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    has_credits: bool = Depends(verify_credits)
):
    # Deduct credits
    current_user.credits -= credits_check.required_credits
    
    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        amount=-credits_check.required_credits,
        type="consumption",
        status="completed"
    )
    db.add(transaction)
    db.commit()
    
    return {"message": "Credits consumed successfully"}

@account_router.post("/oauth/login/{provider}", response_model=Token)
async def oauth_login(
    provider: str,
    token: str,
    db: Session = Depends(get_db)
):
    oauth_handler = OAuthHandler()
    try:
        user_data = await oauth_handler.verify_oauth_token(token, provider)
        
        # Check if user exists
        user = db.query(User).filter(
            (User.oauth_provider == provider) & 
            (User.oauth_id == user_data.oauth_id)
        ).first()
        
        if not user:
            # Create new user if doesn't exist
            user = User(**user_data.dict())
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username}
        )
        return Token(access_token=access_token, token_type="bearer")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
