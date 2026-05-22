from backend.models import User


# REg
def register_user(db, username, email, password):
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
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

    return {
        "status": "success",
        "message": "Registered successfully"
    }


# LOGin
def login_user(db, username, password):
    user = db.query(User).filter(
        User.username == username,
        User.password == password
    ).first()

    if user:
        return {"status": "success", 
                "message": "Login successful",
                "user": user.username}

    return {"status": "error", "message": "Invalid username or password"}