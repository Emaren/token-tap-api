from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Numeric, func
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    wallet_address = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    tokens = relationship("Token", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("TokenTransaction", back_populates="user", cascade="all, delete-orphan")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    symbol = Column(String(10), nullable=False)
    supply = Column(Numeric, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    owner = relationship("User", back_populates="tokens")
    transactions = relationship("TokenTransaction", back_populates="token", cascade="all, delete-orphan")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # 'issue', 'redeem', 'burn'
    amount = Column(Numeric, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    token = relationship("Token", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

