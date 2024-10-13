import os
from hashlib import sha256

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.user import Login, User

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# SQLModel.metadata.create_all(engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)


@app.on_event("startup")
def startup_event():
    SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"docs": "/docs", "redoc": "/redoc"}


@app.post("/register")
def register(user: User):
    if len(user.password) < 10:
        return {"error": "The password must be at least 10 characters long"}

    hashed_password = sha256(user.password.encode()).hexdigest()
    user.password = hashed_password

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"message": "User created successfully", "user": user.to_dict()}


@app.post("/login")
def login(login: Login):
    with Session(engine) as session:
        query = select(User).where(User.email == login.email)
        user = session.exec(query).first()

        if not user:
            return {"error": "User not found"}

        hashed_password = sha256(login.password.encode()).hexdigest()

        if user.password != hashed_password:
            return {"error": "Incorrect password"}

    return {"message": "Login successful", "user": user.to_dict()}
