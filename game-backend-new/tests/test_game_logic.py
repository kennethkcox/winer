import pytest
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from typing import Optional
from game_models import Player, Vineyard, Grape, Must, WineInProduction, Wine, WineryVessel, Base, DBPlayer, DBVineyard, DBGrape, DBMust, DBWineInProduction, DBWine, DBWineryVessel, DBWinery, DBGameState
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_logic.db"
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

@pytest.fixture
def game_instance(db: Session):
    game = Game(db)
    game._initialize_game_state_if_empty()
    return game

def test_game_initialization(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_winery = db.query(DBWinery).first()
    db_vineyard = db.query(DBVineyard).first()
    db_game_state = db.query(DBGameState).first()

    assert db_player is not None
    assert db_player.money == 100000
    assert db_player.reputation == 50
    assert len(db_player.vineyards) == 1
    assert db_player.vineyards[0].name == "Home Block"
    assert db_winery is not None
    assert len(db_winery.vessels) == 5
    assert db_game_state.current_year == 2025
    assert db_game_state.current_month_index == 0

def test_advance_month_within_year(game_instance, db: Session):
    initial_month = db.query(DBGameState).first().current_month_index
    initial_year = db.query(DBGameState).first().current_year
    game_instance.advance_month()
    db.refresh(db.query(DBGameState).first())
    assert db.query(DBGameState).first().current_month_index == initial_month + 1
    assert db.query(DBGameState).first().current_year == initial_year

def test_advance_month_new_year(game_instance, db: Session):
    db_game_state = db.query(DBGameState).first()
    db_game_state.current_month_index = 11  # Set to December
    db.commit()
    initial_year = db_game_state.current_year
    game_instance.advance_month()
    db.refresh(db_game_state)
    db.refresh(db.query(DBPlayer).first().vineyards[0])
    assert db_game_state.current_month_index == 0
    assert db_game_state.current_year == initial_year + 1
    assert not db.query(DBPlayer).first().vineyards[0].harvested_this_year
    assert not db.query(DBPlayer).first().vineyards[0].grapes_ready

def test_buy_vineyard_success(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    initial_money = db_player.money
    initial_reputation = db_player.reputation
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game_instance.buy_vineyard(vineyard_data, "Jura Savagnin")
    assert new_vineyard is not None
    assert new_vineyard.name == "Jura Savagnin"
    db.refresh(db_player)
    assert db_player.money < initial_money
    assert db_player.reputation == initial_reputation + 2
    assert db.query(DBVineyard).filter(DBVineyard.name == "Jura Savagnin").first() is not None

def test_buy_vineyard_not_enough_money(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_player.money = 10000 # Set low money
    db.commit()
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game_instance.buy_vineyard(vineyard_data, "Jura Savagnin")
    assert new_vineyard is None
    assert len(db.query(DBPlayer).first().vineyards) == 1 # Still only the initial vineyard

def test_tend_vineyard_success(game_instance, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    vineyard_name = db_vineyard.name
    initial_health = db_vineyard.health
    db_player = db.query(DBPlayer).first()
    initial_money = db_player.money
    success = game_instance.tend_vineyard(vineyard_name)
    assert success
    db.refresh(db_vineyard)
    db.refresh(db_player)
    assert db_vineyard.health > initial_health
    assert db_player.money == initial_money - 500

def test_tend_vineyard_not_enough_money(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_player.money = 100 # Not enough to tend
    db.commit()
    db_vineyard = db.query(DBVineyard).first()
    initial_health = db_vineyard.health
    success = game_instance.tend_vineyard(db_vineyard.name)
    assert not success
    db.refresh(db_vineyard)
    assert db_vineyard.health == initial_health

def test_harvest_grapes_success(game_instance, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    db_vineyard.grapes_ready = True
    db.commit()
    db_player = db.query(DBPlayer).first()
    initial_grapes_count = len(db_player.grapes_inventory)
    initial_reputation = db_player.reputation
    harvested_grapes = game_instance.harvest_grapes(db_vineyard.name)
    assert harvested_grapes is not None
    assert harvested_grapes.varietal == db_vineyard.varietal
    assert harvested_grapes.vintage == db.query(DBGameState).first().current_year
    db.refresh(db_player)
    assert len(db_player.grapes_inventory) == initial_grapes_count + 1
    db.refresh(db_vineyard)
    assert db_vineyard.harvested_this_year
    assert not db_vineyard.grapes_ready
    assert db_player.reputation == initial_reputation + 5

def test_harvest_grapes_not_ready(game_instance, db: Session):
    db_vineyard = db.query(DBVineyard).first()
    db_vineyard.grapes_ready = False # Not ready
    db.commit()
    harvested_grapes = game_instance.harvest_grapes(db_vineyard.name)
    assert harvested_grapes is None

def test_buy_vessel_success(game_instance, db: Session):
    db_winery = db.query(DBWinery).first()
    initial_vessel_count = len(db_winery.vessels)
    db_player = db.query(DBPlayer).first()
    initial_money = db_player.money
    new_vessel = game_instance.buy_vessel("Concrete Egg")
    assert new_vessel is not None
    assert new_vessel.type == "Concrete Egg"
    db.refresh(db_winery)
    db.refresh(db_player)
    assert len(db_winery.vessels) == initial_vessel_count + 1
    assert db_player.money < initial_money

def test_buy_vessel_not_enough_money(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_player.money = 100 # Not enough
    db.commit()
    new_vessel = game_instance.buy_vessel("Concrete Egg")
    assert new_vessel is None

def test_process_grapes_success(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    # Add some grapes to inventory for testing
    new_grape = DBGrape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, player_id=db_player.id)
    db.add(new_grape)
    db.commit()
    db.refresh(db_player)

    initial_grapes_count = len(db_player.grapes_inventory)
    db_winery = db.query(DBWinery).first()
    initial_must_count = len(db_winery.must_in_production)

    processed_must = game_instance.process_grapes(0, "yes", "Destemmed/Crushed")
    assert processed_must is not None
    assert processed_must.varietal == "Pinot Noir"
    db.refresh(db_player)
    db.refresh(db_winery)
    assert len(db_player.grapes_inventory) == initial_grapes_count - 1
    assert len(db_winery.must_in_production) == initial_must_count + 1
    assert processed_must.processing_method == "Sorted"

def test_start_fermentation_success(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_winery = db.query(DBWinery).first()
    # Add must and ensure a vessel is available
    new_must = DBMust(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, processing_method="Sorted", destem_crush_method="Destemmed/Crushed", winery_id=db_winery.id)
    db.add(new_must)
    db.commit()
    db.refresh(db_winery)

    initial_must_count = len(db_winery.must_in_production)
    initial_fermenting_count = len(db_winery.wines_fermenting)
    initial_reputation = db_player.reputation

    vessel = db_winery.vessels[0] # Use an existing vessel
    vessel_index = db_winery.vessels.index(vessel)

    wine_in_prod = game_instance.start_fermentation(0, vessel_index) # must_index 0, vessel_index 5 (the new one)
    assert wine_in_prod is not None
    assert wine_in_prod.varietal == "Pinot Noir"
    assert wine_in_prod.stage == "fermenting"
    db.refresh(db_winery)
    db.refresh(db_player)
    db.refresh(vessel)
    assert len(db_winery.must_in_production) == initial_must_count - 1
    assert len(db_winery.wines_fermenting) == initial_fermenting_count + 1
    assert vessel.in_use
    assert db_player.reputation == initial_reputation + 3

def test_perform_maceration_action_success(game_instance, db: Session):
    db_winery = db.query(DBWinery).first()
    # Add a red wine in fermentation
    wine_prod = DBWineInProduction(varietal="Pinot Noir", vintage=2025, quantity_liters=300, quality=70, vessel_type="Open Top Fermenter", vessel_index=1, stage="fermenting", winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    wine_prod_index = db_winery.wines_fermenting.index(wine_prod)
    initial_quality = wine_prod.quality
    success = game_instance.perform_maceration_action(wine_prod_index, "punch_down")
    assert success
    db.refresh(wine_prod)
    assert wine_prod.quality > initial_quality
    assert wine_prod.maceration_actions_taken == 1

def test_start_aging_success(game_instance, db: Session):
    db_winery = db.query(DBWinery).first()
    # Add a fermented wine and an aging vessel
    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2025, quantity_liters=200, quality=80, vessel_type="Stainless Steel Tank", vessel_index=0, stage="fermenting", fermentation_progress=100, winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    initial_fermenting_count = len(db_winery.wines_fermenting)
    initial_aging_count = len(db_winery.wines_aging)

    vessel = db_winery.vessels[1] # Use another existing vessel for aging
    vessel_index = db_winery.vessels.index(vessel)

    wine_in_prod = game_instance.start_aging(0, vessel_index) # wine_prod_index 0, vessel_index 5 (the new one), 6 months aging
    assert wine_in_prod is not None
    assert wine_in_prod.stage == "aging"
    db.refresh(db_winery)
    db.refresh(wine_prod)
    db.refresh(vessel)
    assert len(db_winery.wines_fermenting) == initial_fermenting_count - 1
    assert len(db_winery.wines_aging) == initial_aging_count + 1
    assert vessel.in_use

def test_bottle_wine_success(game_instance, db: Session):
    db_player = db.query(DBPlayer).first()
    db_winery = db.query(DBWinery).first()
    # Add an aged wine
    vessel = db_winery.vessels[2] # Use an existing vessel
    vessel.in_use = True # Manually set to in_use for test setup
    db.commit()
    db.refresh(vessel)

    wine_prod = DBWineInProduction(varietal="Chardonnay", vintage=2024, quantity_liters=750, quality=85, vessel_type=vessel.type, vessel_index=db_winery.vessels.index(vessel), stage="aging", aging_progress=12, aging_duration=12, winery_id=db_winery.id)
    db.add(wine_prod)
    db.commit()
    db.refresh(db_winery)

    initial_aging_count = len(db_winery.wines_aging)
    initial_bottled_count = len(db_player.bottled_wines)
    initial_reputation = db_player.reputation

    bottled_wine = game_instance.bottle_wine(0, "My Great Chardonnay")
    assert bottled_wine is not None
    assert bottled_wine.name == "My Great Chardonnay"
    assert bottled_wine.bottles == 1000 # 750L / 0.75L per bottle
    db.refresh(db_player)
    db.refresh(db_winery)
    db.refresh(vessel)
    assert len(db_winery.wines_aging) == initial_aging_count - 1
    assert len(db_player.bottled_wines) == initial_bottled_count + 1
    assert not vessel.in_use
    assert db_player.reputation == initial_reputation + 10

def test_get_available_vineyards_for_purchase(game_instance):
    vineyards = game_instance.get_available_vineyards_for_purchase()
    assert isinstance(vineyards, list)
    assert len(vineyards) > 0
    assert "region" in vineyards[0]
    assert "varietal" in vineyards[0]
    assert "cost" in vineyards[0]

def test_get_available_vessel_types_for_purchase(game_instance):
    vessels = game_instance.get_available_vessel_types_for_purchase()
    assert isinstance(vessels, list)
    assert len(vessels) > 0
    assert "name" in vessels[0]
    assert "capacity" in vessels[0]
    assert "cost" in vessels[0]
    assert "type" in vessels[0]
