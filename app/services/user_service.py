from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserLogin, TokenResponse
from app.core.security import  verify_password, hash_password
from app.utils.jwt import create_access_token
from fastapi import HTTPException

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    
        # Hash the password
        hashed_password = hash_password(user.password)

        # Create user instance
        new_user = User(
            email=user.email,
            username=user.username,
            role=user.role if user.role else "patient",
            phone_number=user.phone_number,
            age=user.age,
            password=hashed_password,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def login_user(user: UserLogin, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, str(db_user.password)):  # Ensure password is a string
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(user_id=db_user.id)
    return {"access_token": access_token, "token_type": "bearer"}