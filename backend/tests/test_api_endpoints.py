import pytest
from fastapi.testclient import TestClient
from main import app, get_db, api_router, initialize_database, get_current_user, lifespan
from fastapi import FastAPI
from game_logic import Game
from typing import Optional
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    BuyVineyardRequest, TendVineyardRequest, HarvestGrapesRequest, BuyVesselRequest,
    ProcessGrapesRequest, StartFermentationRequest, PerformMacerationActionRequest,
    StartAgingRequest, BottleWineRequest,
    Base, DBPlayer, DBVineyard, DBWinery, DBGrape, DBMust, DBWineInProduction, DBWine, DBWineryVessel, DBGameState
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db")
def db_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

test_app = FastAPI(lifespan=lifespan)
test_app.include_router(api_router, prefix="/api")

@pytest.fixture(name="client")
def client_fixture(db: Session):
    def override_get_db():
        yield db

    def override_get_current_user():
        return db.query(DBPlayer).first()

    initialize_database(db)
    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = override_get_current_user
    client = TestClient(test_app)
    yield client
    test_app.dependency_overrides.clear()

def test_read_root(client):
    response = client.get("/api")
    assert response.status_code == 200
    assert "player" in response.json()
    assert "current_year" in response.json()

def test_advance_month_endpoint(client, db: Session):
    response = client.post("/api/advance_month")
    assert response.status_code == 200
    assert "player" in response.json()
    # Verify state change in DB
    db_game_state = db.query(DBGameState).first()
    assert db_game_state.current_month_index == 1 # Should advance by one month

def test_get_player(client):
    response = client.get("/api/player")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "money" in response.json()

def test_get_vineyards(client):
    response = client.get("/api/vineyards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1 # Initial vineyard

def test_get_winery(client):
    response = client.get("/api/winery")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "vessels" in response.json()

def test_buy_vineyard_endpoint_success(client, db: Session):
    db_player = db.query(DBPlayer).first()
    initial_money = db_player.money
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    request_body = BuyVineyardRequest(vineyard_data=vineyard_data, vineyard_name="Test Vineyard")
    response = client.post("/api/buy_vineyard", json=request_body.model_dump())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Vineyard"
    db.refresh(db_player)
    assert db_player.money < initial_money
    assert db.query(DBVineyard).filter(DBVineyard.name == "Test Vineyard").first() is not None

def test_buy_vineyard_endpoint_not_enough_money(client, db: Session):
    db_player = db.query(DBPlayer).first()
    db_player.money = 10000 # Set low money
    db.commit()
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    request_body = BuyVineyardRequest(vineyard_data=vineyard_data, vineyard_name="Test Vineyard")
    response = client.post("/api/buy_vineyard", json=request_body.model_dump())
    assert response.status_code == 400
    assert "Not enough money" in response.json()["detail"]
    assert db.query(DBVineyard).filter(DBVineyard.name == "Test Vineyard").first() is None

def test_tend_vineyard_endpoint_success(client, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    vineyard_name = db_vineyard.name
    initial_health = db_vineyard.health
    request_body = TendVineyardRequest(vineyard_name=vineyard_name)
    response = client.post("/api/tend_vineyard", json=request_body.model_dump())
    assert response.status_code == 200
    assert "Successfully tended" in response.json()["message"]
    db.refresh(db_vineyard)
    assert db_vineyard.health > initial_health

def test_harvest_grapes_endpoint_success(client, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    db_vineyard.grapes_ready = True # Manually set for test
    db.commit()
    request_body = HarvestGrapesRequest(vineyard_name=db_vineyard.name)
    response = client.post("/api/harvest_grapes", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()
    db.refresh(db_vineyard)
    assert not db_vineyard.grapes_ready
    assert db_vineyard.harvested_this_year
    assert db.query(DBGrape).filter(DBGrape.varietal == db_vineyard.varietal).first() is not None

def test_buy_vessel_endpoint_success(client, db: Session):
    db_winery = db.query(DBWinery).first()
    initial_vessel_count = len(db_winery.vessels)
    request_body = BuyVesselRequest(vessel_type_name="Concrete Egg")
    response = client.post("/api/buy_vessel", json=request_body.model_dump())
    assert response.status_code == 200
    db.refresh(db_winery)
    assert len(db_winery.vessels) == initial_vessel_count + 1

def test_process_grapes_endpoint_success(client, db: Session):
    db_player = db.query(DBPlayer).first()
    new_grape = DBGrape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, player_id=db_player.id)
    db.add(new_grape)
    db.commit()
    db.refresh(db_player)

    initial_grapes_count = len(db_player.grapes_inventory)
    request_body = ProcessGrapesRequest(grape_index=0, sort_choice="no", destem_crush_method="Destemmed/Crushed")
    response = client.post("/api/process_grapes", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()
    db.refresh(db_player)
    assert len(db_player.grapes_inventory) == initial_grapes_count - 1
    assert db.query(DBMust).filter(DBMust.varietal == "Pinot Noir").first() is not None

def test_start_fermentation_endpoint_success(client, db: Session):
    db_player = db.query(DBPlayer).first()
    db_winery = db.query(DBWinery).first()
    new_must = DBMust(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, processing_method="Sorted", destem_crush_method="Destemmed/Crushed", winery_id=db_winery.id)
    db.add(new_must)
    db.commit()
    db.refresh(db_winery)

    vessel = db_winery.vessels[0] # Use an existing vessel
    vessel_index = db_winery.vessels.index(vessel)

    request_body = StartFermentationRequest(must_index=0, vessel_index=vessel_index)
    response = client.post("/api/start_fermentation", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()
    db.refresh(db_winery)
    db.refresh(vessel)
    assert db.query(DBMust).filter(DBMust.id == new_must.id).first() is None
    assert len(db_winery.wines_fermenting) == 1
    assert vessel.in_use

def test_perform_maceration_action_endpoint_success(client, db: Session):
    db_winery = db.query(DBWinery).first()
    wine_prod = DBWineInProduction(varietal="Pinot Noir", vintage=2025, quantity_liters=300, quality=70, vessel_type="Open Top Fermenter", vessel_index=1, stage="fermenting", winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    wine_prod_index = db_winery.wines_fermenting.index(wine_prod)
    initial_quality = wine_prod.quality
    request_body = PerformMacerationActionRequest(wine_prod_index=wine_prod_index, action_type="punch_down")
    response = client.post("/api/perform_maceration_action", json=request_body.model_dump())
    assert response.status_code == 200
    assert "message" in response.json()
    db.refresh(wine_prod)
    assert wine_prod.quality > initial_quality
    assert wine_prod.maceration_actions_taken == 1

def test_start_aging_endpoint_success(client, db: Session):
    db_winery = db.query(DBWinery).first()
    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2025, quantity_liters=200, quality=80, vessel_type="Stainless Steel Tank", vessel_index=0, stage="fermenting", fermentation_progress=100, winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    wine_prod_index = db_winery.wines_fermenting.index(wine_prod)
    vessel = db_winery.vessels[1] # Use another existing vessel for aging
    vessel_index = db_winery.vessels.index(vessel)

    request_body = StartAgingRequest(wine_prod_index=wine_prod_index, vessel_index=vessel_index, aging_duration=6)
    response = client.post("/api/start_aging", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()
    db.refresh(db_winery)
    db.refresh(wine_prod)
    db.refresh(vessel)
    assert wine_prod.stage == "aging"
    assert vessel.in_use
    assert not db.query(DBWineInProduction).filter(DBWineInProduction.id == wine_prod.id, DBWineInProduction.stage == "fermenting").first()
    assert len(db_winery.wines_aging) == 1

def test_bottle_wine_endpoint_success(client, db: Session):
    db_player = db.query(DBPlayer).first()
    db_winery = db.query(DBWinery).first()
    vessel = db_winery.vessels[2] # Use an existing vessel
    vessel.in_use = True # Manually set to in_use for test setup
    db.commit()
    db.refresh(vessel)

    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2024, quantity_liters=750, quality=85, vessel_type=vessel.type, vessel_index=db_winery.vessels.index(vessel), stage="aging", aging_progress=12, aging_duration=12, winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    wine_prod_index = db_winery.wines_aging.index(wine_prod)
    request_body = BottleWineRequest(wine_prod_index=wine_prod_index, wine_name="My Test Wine")
    response = client.post("/api/bottle_wine", json=request_body.model_dump())
    assert response.status_code == 200
    assert "name" in response.json()
    db.refresh(db_player)
    db.refresh(db_winery)
    db.refresh(vessel)
    assert len(db_player.bottled_wines) == 1
    assert not vessel.in_use
    assert not db.query(DBWineInProduction).filter(DBWineInProduction.id == wine_prod.id).first()
