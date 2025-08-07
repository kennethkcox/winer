import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Set environment variable before importing the app
os.environ['SECRET_KEY'] = 'test_secret'

from main import app, get_db
from services import GameService
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    BuyVineyardRequest, TendVineyardRequest, HarvestGrapesRequest, BuyVesselRequest,
    ProcessGrapesRequest, StartFermentationRequest, PerformMacerationActionRequest,
    StartAgingRequest, BottleWineRequest,
    Base, DBPlayer, DBVineyard, DBWinery, DBGrape, DBMust, DBWineInProduction, DBWine, DBWineryVessel, DBGameState
)

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Initialize game state once per module
    game_service = GameService(db)
    game_service._initialize_game_state_if_empty()
    yield db
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db: Session):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db

    # Get a token
    login_response = TestClient(app).post("/token", data={"username": "testuser", "password": "password"})
    token = login_response.json()["access_token"]

    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {token}"
    yield client
    app.dependency_overrides.clear()

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "player" in response.json()
    assert "current_year" in response.json()

def test_advance_month_endpoint(client, db: Session):
    response = client.post("/advance_month")
    assert response.status_code == 200
    assert "player" in response.json()
    db_game_state = db.query(DBGameState).first()
    assert db_game_state.current_month_index == 1

def test_get_player(client):
    response = client.get("/player")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "money" in response.json()

def test_get_vineyards(client):
    response = client.get("/vineyards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_winery(client):
    response = client.get("/winery")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "vessels" in response.json()

def test_buy_vineyard_endpoint_success(client, db: Session):
    db_player = db.query(DBPlayer).first()
    initial_money = db_player.money
    request_body = {"region": "Jura", "varietal": "Savagnin", "vineyard_name": "Test Vineyard"}
    response = client.post("/buy_vineyard", json=request_body)
    assert response.status_code == 200
    data = response.json()
    assert data["new_vineyard"]["name"] == "Test Vineyard"
    db.refresh(db_player)
    assert db_player.money < initial_money
    assert db.query(DBVineyard).filter(DBVineyard.name == "Test Vineyard").first() is not None

def test_buy_vineyard_endpoint_not_enough_money(client, db: Session):
    db_player = db.query(DBPlayer).first()
    original_money = db_player.money
    db_player.money = 100 # Set low money
    db.commit()

    request_body = {"region": "Jura", "varietal": "Savagnin", "vineyard_name": "Expensive Vineyard"}
    response = client.post("/buy_vineyard", json=request_body)
    assert response.status_code == 400
    assert "Not enough money" in response.json()["detail"]
    assert db.query(DBVineyard).filter(DBVineyard.name == "Expensive Vineyard").first() is None

    # Reset money
    db_player.money = original_money
    db.commit()

def test_tend_vineyard_endpoint_success(client, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    vineyard_name = db_vineyard.name
    initial_health = db_vineyard.health
    response = client.post("/tend_vineyard", json={"vineyard_name": vineyard_name})
    assert response.status_code == 200
    assert "Successfully tended" in response.json()["message"]
    db.refresh(db_vineyard)
    assert db_vineyard.health > initial_health

# Note: More tests would be needed here to cover all endpoints and logic.
# This refactoring serves as a template for how to structure the tests correctly.
