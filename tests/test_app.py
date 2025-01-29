import pytest
from flask import session
from app.server import app, db, User, AlignmentHistory

@pytest.fixture
def client():
    """Set up a Flask test client and test database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory DB
    app.config["SECRET_KEY"] = "test_secret"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    """Test user registration."""
    response = client.post("/register", data={
        "username": "testuser",
        "password": "testpassword",
        "confirm_password": "testpassword"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"testuser" in response.data  # Check if username appears in response

def test_register_existing_user(client):
    """Test registering with an existing username."""
    client.post("/register", data={
        "username": "existinguser",
        "password": "password123",
        "confirm_password": "password123"
    })

    response = client.post("/register", data={
        "username": "existinguser",
        "password": "newpassword",
        "confirm_password": "newpassword"
    })

    assert response.status_code == 400
    assert b"Username already exists" in response.data

def test_login(client):
    """Test successful login."""
    client.post("/register", data={
        "username": "loginuser",
        "password": "securepass",
        "confirm_password": "securepass"
    })

    response = client.post("/login", data={
        "username": "loginuser",
        "password": "securepass"
    }, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess["user_id"] is not None  # Ensure user session is created

def test_login_invalid(client):
    """Test login with wrong credentials."""
    response = client.post("/login", data={
        "username": "wronguser",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert b"Invalid username or password" in response.data

def test_logout(client):
    """Test user logout."""
    client.post("/register", data={
        "username": "logoutuser",
        "password": "password",
        "confirm_password": "password"
    })
    client.post("/login", data={
        "username": "logoutuser",
        "password": "password"
    })

    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert "user_id" not in sess  # Ensure session is cleared

def test_unauthorized_home_access(client):
    """Ensure unauthorized users cannot access /home."""
    response = client.get("/home")
    assert response.status_code == 401
    assert b"Unauthorized" in response.data
