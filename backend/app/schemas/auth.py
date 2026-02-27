from pydantic import BaseModel


class PhoneRegisterRequest(BaseModel):
    phone_number: str


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    phone_number: str
    nickname: str | None
    coupon_balance: int
    daily_free_pulls_used: int

    model_config = {"from_attributes": True}
