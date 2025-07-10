import pytest
from fastapi.testclient import TestClient
from main import app
from game_logic import Game
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    BuyVineyardRequest, TendVineyardRequest, HarvestGrapesRequest, BuyVesselRequest,
    ProcessGrapesRequest, StartFermentationRequest, PerformMacerationActionRequest,
    StartAgingRequest, BottleWineRequest
)
from typing import List, Dict, Any

@pytest.fixture
def client():
    # Reset the game instance for each test
    app.game_instance = Game()
    return TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "player" in response.json()
    assert "current_year" in response.json()

def test_advance_month_endpoint(client):
    response = client.post("/advance_month")
    assert response.status_code == 200
    assert "player" in response.json()

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

def test_buy_vineyard_endpoint_success(client):
    initial_money = client.app.game_instance.player.money
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    request_body = BuyVineyardRequest(vineyard_data=vineyard_data, vineyard_name="Test Vineyard")
    response = client.post("/buy_vineyard", json=request_body.model_dump())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Vineyard"
    assert client.app.game_instance.player.money < initial_money

def test_buy_vineyard_endpoint_not_enough_money(client):
    client.app.game_instance.player.money = 10000 # Set low money
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    request_body = BuyVineyardRequest(vineyard_data=vineyard_data, vineyard_name="Test Vineyard")
    response = client.post("/buy_vineyard", json=request_body.model_dump())
    assert response.status_code == 400
    assert "Not enough money" in response.json()["detail"]

def test_tend_vineyard_endpoint_success(client):
    vineyard_name = client.app.game_instance.player.vineyards[0].name
    request_body = TendVineyardRequest(vineyard_name=vineyard_name)
    response = client.post("/tend_vineyard", json=request_body.model_dump())
    assert response.status_code == 200
    assert "Successfully tended" in response.json()["message"]

def test_harvest_grapes_endpoint_success(client):
    vineyard = client.app.game_instance.player.vineyards[0]
    vineyard.grapes_ready = True # Manually set for test
    request_body = HarvestGrapesRequest(vineyard_name=vineyard.name)
    response = client.post("/harvest_grapes", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()

def test_buy_vessel_endpoint_success(client):
    initial_vessel_count = len(client.app.game_instance.player.winery.vessels)
    request_body = BuyVesselRequest(vessel_type_name="Concrete Egg")
    response = client.post("/buy_vessel", json=request_body.model_dump())
    assert response.status_code == 200
    assert len(response.json()["vessels"]) == initial_vessel_count + 1

def test_process_grapes_endpoint_success(client):
    client.app.game_instance.player.grapes_inventory.append(Grape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70))
    request_body = ProcessGrapesRequest(grape_index=0, sort_choice="no", destem_crush_method="Destemmed/Crushed")
    response = client.post("/process_grapes", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()

def test_start_fermentation_endpoint_success(client):
    client.app.game_instance.player.grapes_inventory.append(Grape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70))
    client.app.game_instance.process_grapes(0, "no", "Destemmed/Crushed") # Process grapes to create must
    request_body = StartFermentationRequest(must_index=0, vessel_index=0)
    response = client.post("/start_fermentation", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()

def test_perform_maceration_action_endpoint_success(client):
    client.app.game_instance.player.winery.wines_fermenting.append(WineInProduction(varietal="Pinot Noir", vintage=2025, quantity_liters=300, quality=70, vessel_type="Open Top Fermenter", vessel_index=1, stage="fermenting"))
    request_body = PerformMacerationActionRequest(wine_prod_index=0, action_type="punch_down")
    response = client.post("/perform_maceration_action", json=request_body.model_dump())
    assert response.status_code == 200
    assert "message" in response.json()

def test_start_aging_endpoint_success(client):
    client.app.game_instance.player.winery.wines_fermenting.append(WineInProduction(varietal="Chardonnay", vintage=2025, quantity_liters=200, quality=80, vessel_type="Stainless Steel Tank", vessel_index=0, stage="fermenting", fermentation_progress=100))
    request_body = StartAgingRequest(wine_prod_index=0, vessel_index=0, aging_duration=6)
    response = client.post("/start_aging", json=request_body.model_dump())
    assert response.status_code == 200
    assert "varietal" in response.json()

def test_bottle_wine_endpoint_success(client):
    client.app.game_instance.player.winery.wines_aging.append(WineInProduction(varietal="Chardonnay", vintage=2024, quantity_liters=750, quality=85, vessel_type="Neutral Oak Barrel (225L)", vessel_index=2, stage="aging", aging_progress=12, aging_duration=12))
    request_body = BottleWineRequest(wine_prod_index=0, wine_name="My Test Wine")
    response = client.post("/bottle_wine", json=request_body.model_dump())
    assert response.status_code == 200
    assert "name" in response.json()