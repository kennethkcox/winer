import pytest
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    DBPlayer, DBVineyard, DBWinery, DBGrape, DBMust, DBWineInProduction, DBWine, DBWineryVessel, DBGameState, Base
)
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from main import initialize_database

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def game_instance(db_session: Session):
    initialize_database(db_session)
    return Game(db_session)

def test_game_initialization(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_winery = db_session.query(DBWinery).first()
    db_vineyard = db_session.query(DBVineyard).first()
    db_game_state = db_session.query(DBGameState).first()

    assert db_player is not None
    assert db_winery is not None
    assert db_vineyard is not None
    assert db_game_state is not None
    assert db_player.name == "Winemaker"
    assert db_winery.name == "Main Winery"
    assert db_vineyard.name == "Home Block"

def test_advance_month_within_year(game_instance, db_session: Session):
    initial_month = db_session.query(DBGameState).first().current_month_index
    game_instance.advance_month()
    new_month = db_session.query(DBGameState).first().current_month_index
    assert new_month == initial_month + 1

def test_advance_month_new_year(game_instance, db_session: Session):
    db_game_state = db_session.query(DBGameState).first()
    db_game_state.current_month_index = 11  # Set to December
    db_session.commit()
    initial_year = db_game_state.current_year
    game_instance.advance_month()
    db_session.refresh(db_game_state)
    assert db_game_state.current_month_index == 0
    assert db_game_state.current_year == initial_year + 1

def test_buy_vineyard_success(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    initial_money = db_player.money
    initial_vineyard_count = len(db_player.vineyards)
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game_instance.buy_vineyard(vineyard_data, "Test Jura Vineyard")
    db_session.refresh(db_player)
    assert new_vineyard is not None
    assert db_player.money < initial_money
    assert len(db_player.vineyards) == initial_vineyard_count + 1

def test_buy_vineyard_not_enough_money(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_player.money = 10000 # Set low money
    db_session.commit()
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game_instance.buy_vineyard(vineyard_data, "Test Jura Vineyard")
    assert new_vineyard is None

def test_tend_vineyard_success(game_instance, db_session: Session):
    db_vineyard = db_session.query(DBVineyard).first()
    vineyard_name = db_vineyard.name
    initial_health = db_vineyard.health
    result = game_instance.tend_vineyard(vineyard_name)
    db_session.refresh(db_vineyard)
    assert result is True
    assert db_vineyard.health > initial_health

def test_tend_vineyard_not_enough_money(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_player.money = 100 # Not enough to tend
    db_session.commit()
    db_vineyard = db_session.query(DBVineyard).first()
    result = game_instance.tend_vineyard(db_vineyard.name)
    assert result is False

def test_harvest_grapes_success(game_instance, db_session: Session):
    db_vineyard = db_session.query(DBVineyard).first()
    db_vineyard.grapes_ready = True
    db_session.commit()
    harvested_grapes = game_instance.harvest_grapes(db_vineyard.name)
    db_session.refresh(db_vineyard)
    assert harvested_grapes is not None
    assert harvested_grapes.varietal == db_vineyard.varietal
    assert not db_vineyard.grapes_ready
    assert db_vineyard.harvested_this_year

def test_harvest_grapes_not_ready(game_instance, db_session: Session):
    db_vineyard = db_session.query(DBVineyard).first()
    db_vineyard.grapes_ready = False # Not ready
    db_session.commit()
    harvested_grapes = game_instance.harvest_grapes(db_vineyard.name)
    assert harvested_grapes is None

def test_buy_vessel_success(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_player.money = 100000
    db_session.commit()
    db_winery = db_session.query(DBWinery).first()
    initial_vessel_count = len(db_winery.vessels)
    new_vessel = game_instance.buy_vessel("Concrete Egg")
    db_session.refresh(db_winery)
    assert new_vessel is not None
    assert len(db_winery.vessels) == initial_vessel_count + 1

def test_buy_vessel_not_enough_money(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_player.money = 100 # Not enough
    db_session.commit()
    new_vessel = game_instance.buy_vessel("Concrete Egg")
    assert new_vessel is None

def test_process_grapes_success(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    # Add some grapes to inventory for testing
    new_grape = DBGrape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, player_id=db_player.id)
    db_session.add(new_grape)
    db_session.commit()
    db_session.refresh(db_player)

    initial_grapes_count = len(db_player.grapes_inventory)
    processed_must = game_instance.process_grapes(0, "no", "Destemmed/Crushed")
    db_session.refresh(db_player)

    assert processed_must is not None
    assert len(db_player.grapes_inventory) == initial_grapes_count - 1
    assert db_session.query(DBMust).filter(DBMust.varietal == "Pinot Noir").first() is not None

def test_start_fermentation_success(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_winery = db_session.query(DBWinery).first()
    # Add must and ensure a vessel is available
    new_must = DBMust(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, processing_method="Sorted", destem_crush_method="Destemmed/Crushed", winery_id=db_winery.id)
    db_session.add(new_must)
    db_session.commit()
    db_session.refresh(db_winery)

    vessel = db_winery.vessels[0]
    vessel_index = db_winery.vessels.index(vessel)

    wine_in_prod = game_instance.start_fermentation(0, vessel_index)
    db_session.refresh(db_winery)
    db_session.refresh(vessel)

    assert wine_in_prod is not None
    assert db_session.query(DBMust).filter(DBMust.id == new_must.id).first() is None
    assert len(db_winery.wines_fermenting) == 1
    assert vessel.in_use

def test_perform_maceration_action_success(game_instance, db_session: Session):
    db_winery = db_session.query(DBWinery).first()
    # Add a red wine in fermentation
    wine_prod = DBWineInProduction(varietal="Pinot Noir", vintage=2025, quantity_liters=300, quality=70, vessel_type="Open Top Fermenter", vessel_index=1, stage="fermenting", winery_id=db_winery.id)
    db_session.add(wine_prod)
    db_session.commit()
    db_session.refresh(db_winery)

    wine_prod_index = db_winery.wines_fermenting.index(wine_prod)
    initial_quality = wine_prod.quality

    result = game_instance.perform_maceration_action(wine_prod_index, "punch_down")
    db_session.refresh(wine_prod)

    assert result is True
    assert wine_prod.quality > initial_quality
    assert wine_prod.maceration_actions_taken == 1

def test_start_aging_success(game_instance, db_session: Session):
    db_winery = db_session.query(DBWinery).first()
    # Add a fermented wine and an aging vessel
    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2025, quantity_liters=200, quality=80, vessel_type="Stainless Steel Tank", vessel_index=0, stage="fermenting", fermentation_progress=100, winery_id=db_winery.id)
    db_session.add(wine_prod)
    db_session.commit()
    db_session.refresh(db_winery)

    wine_prod_index = db_winery.wines_fermenting.index(wine_prod)
    vessel = db_winery.vessels[2]
    vessel_index = db_winery.vessels.index(vessel)

    aged_wine = game_instance.start_aging(wine_prod_index, vessel_index)
    assert aged_wine is not None
    db_session.refresh(db_winery)
    db_session.refresh(vessel)
    assert aged_wine.stage == "aging"
    assert vessel.in_use
    assert not db_session.query(DBWineInProduction).filter(DBWineInProduction.id == aged_wine.id, DBWineInProduction.stage == "fermenting").first()
    assert len(db_winery.wines_aging) == 1

def test_bottle_wine_success(game_instance, db_session: Session):
    db_player = db_session.query(DBPlayer).first()
    db_winery = db_session.query(DBWinery).first()
    # Add an aged wine
    vessel = db_winery.vessels[2]
    vessel.in_use = True
    db_session.commit()
    db_session.refresh(vessel)

    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2024, quantity_liters=750, quality=85, vessel_type=vessel.type, vessel_index=db_winery.vessels.index(vessel), stage="aging", aging_progress=12, aging_duration=12, winery_id=db_winery.id)
    db_session.add(wine_prod)
    db_session.commit()
    db_session.refresh(db_winery)

    wine_prod_index = db_winery.wines_aging.index(wine_prod)
    bottled_wine = game_instance.bottle_wine(wine_prod_index, "My Test Chardonnay")
    db_session.refresh(db_player)
    db_session.refresh(db_winery)
    db_session.refresh(vessel)

    assert bottled_wine is not None
    assert len(db_player.bottled_wines) == 1
    assert not vessel.in_use
    assert not db_session.query(DBWineInProduction).filter(DBWineInProduction.id == wine_prod.id).first()

def test_get_available_vineyards_for_purchase(game_instance):
    available = game_instance.get_available_vineyards_for_purchase()
    assert isinstance(available, list)
    assert len(available) > 0
    assert "region" in available[0]
    assert "varietal" in available[0]

def test_get_available_vessel_types_for_purchase(game_instance):
    available = game_instance.get_available_vessel_types_for_purchase()
    assert isinstance(available, list)
    assert len(available) > 0
    assert "name" in available[0]
    assert "cost" in available[0]
