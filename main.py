from hashlib import sha256

from sqlmodel import Session, SQLModel, create_engine, select

from fastapi import FastAPI
from models.user import Login, User

app = FastAPI()

DATABASE_URL = "postgresql://boinho_3cgu_user:rqABTPCpbl1orYDSLK3J0wWmG5cF86o2@dpg-cs5cif08fa8c73akcqo0-a.oregon-postgres.render.com/boinho_3cgu"

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)


@app.get("/")
def root():
    return {"docs": "/docs", "redoc": "/redoc"}


@app.post("/register")
def post_user(user: User):
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
        query = select(User).where(User.username == login.username)
        user = session.exec(query).first()

        if not user:
            return {"error": "User not found"}

        hashed_password = sha256(login.password.encode()).hexdigest()

        if user.password != hashed_password:
            return {"error": "Incorrect password"}

    return {"message": "Login successful", "user": user.to_dict()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
