import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from main import app, get_db
from game_models import Base, DBPlayer, DBWine
from services import GameService

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Create a test player and wine
    player = DBPlayer(id=1, name="Test Player", money=1000)
    wine = DBWine(id=1, name="Test Wine", bottles=10, quality=80, player_id=1)
    db.add(player)
    db.add(wine)
    db.commit()
    yield db
    Base.metadata.drop_all(bind=engine)

def test_sell_wine_success(db_session):
    response = client.post("/sell_wine", json={"wine_id": 1, "bottles": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["updated_money"] == 1000 + (80 * 10 * 5)
    assert data["sold_wine_id"] == 1
    assert data["bottles_remaining"] == 5

def test_sell_wine_not_enough_bottles(db_session):
    response = client.post("/sell_wine", json={"wine_id": 1, "bottles": 15})
    assert response.status_code == 400

def test_sell_wine_does_not_exist(db_session):
    response = client.post("/sell_wine", json={"wine_id": 99, "bottles": 5})
    assert response.status_code == 400
