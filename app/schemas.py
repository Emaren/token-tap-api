from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class UserCreate(BaseModel):
    uid: str
    email: Optional[str]
    phone: Optional[str]
    wallet_address: Optional[str]

class TokenCreate(BaseModel):
    name: str
    symbol: str
    owner_id: int

class TokenAction(BaseModel):
    user_id: int
    amount: Decimal

class TokenTransactionOut(BaseModel):
    id: int
    token_id: int
    user_id: int
    action: str
    amount: Decimal
    timestamp: datetime

    class Config:
        from_attributes = True

