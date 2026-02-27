import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import PhoneRegisterRequest, VerifyCodeRequest, TokenResponse
from app.core.security import create_access_token

router = APIRouter()

# In-memory verification codes (use Redis in production)
_verification_codes: dict[str, str] = {}


@router.post("/register", response_model=dict)
async def register(request: PhoneRegisterRequest, db: AsyncSession = Depends(get_db)):
    """Send verification code to phone number."""
    # Generate 6-digit code
    code = f"{random.randint(100000, 999999)}"
    _verification_codes[request.phone_number] = code

    # TODO: Send SMS via Twilio or similar service
    # For MVP, return code in response (dev mode only)
    return {
        "message": "Verification code sent",
        "phone_number": request.phone_number,
        "dev_code": code,  # Remove in production
    }


@router.post("/verify", response_model=TokenResponse)
async def verify(request: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    """Verify phone number and return JWT token."""
    stored_code = _verification_codes.get(request.phone_number)

    if stored_code is None or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    # Remove used code
    del _verification_codes[request.phone_number]

    # Find or create user
    result = await db.execute(
        select(User).where(User.phone_number == request.phone_number)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(phone_number=request.phone_number, phone_verified=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.phone_verified = True
        await db.commit()

    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
