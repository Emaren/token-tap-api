from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal, engine
from app.schemas import UserCreate, TokenCreate, TokenAction, TokenTransactionOut

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"status": "TokenTap API running"}

@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.uid == user.uid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="UID already exists")

    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/tokens/")
def create_token(token: TokenCreate, db: Session = Depends(get_db)):
    db_token = models.Token(**token.dict())
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

@app.post("/tokens/{token_id}/issue")
def issue_token(token_id: int, payload: TokenAction, db: Session = Depends(get_db)):
    token = db.query(models.Token).filter(models.Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    token.supply += payload.amount
    tx = models.TokenTransaction(
        token_id=token_id,
        user_id=payload.user_id,
        action="issue",
        amount=payload.amount
    )
    db.add(tx)
    db.commit()
    return {"status": "issued", "new_supply": token.supply}

@app.post("/tokens/{token_id}/redeem")
def redeem_token(token_id: int, payload: TokenAction, db: Session = Depends(get_db)):
    token = db.query(models.Token).filter(models.Token.id == token_id).first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")

    if token.supply < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient supply")

    token.supply -= payload.amount
    tx = models.TokenTransaction(
        token_id=token_id,
        user_id=payload.user_id,
        action="redeem",
        amount=payload.amount
    )
    db.add(tx)
    db.commit()
    return {"status": "redeemed", "new_supply": token.supply}

@app.get("/tokens/{token_id}/history", response_model=list[TokenTransactionOut])
def view_token_history(token_id: int, db: Session = Depends(get_db)):
    txs = db.query(models.TokenTransaction).filter(
        models.TokenTransaction.token_id == token_id
    ).all()
    return txs

@app.get("/ping")
def ping():
    return {"status": "ok"}
