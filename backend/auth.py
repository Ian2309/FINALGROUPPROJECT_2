from backend.database import SessionLocal
from backend.models import User


def register_user(username, email, password):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.username == username
    ).first()

    if existing_user:
        db.close()

        return {
            "status": "error",
            "message": "Username already exists"
        }

    new_user = User(
        username=username,
        email=email,
        password=password
    )

    db.add(new_user)
    db.commit()

    db.close()

    return {
        "status": "success",
        "message": "Registered successfully"
    }


def login_user(username, password):

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    db.close()

    if user:
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "username": user.username,
                "email": user.email
            }
        }

    return {
        "status": "error",
        "message": "Invalid login"
    }