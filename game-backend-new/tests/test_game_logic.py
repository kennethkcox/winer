import pytest
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from game_models import Player, Vineyard, Grape, Must, WineInProduction, Wine, WineryVessel

# Test for Game class and its methods

def test_game_initialization():
    game = Game()
    assert isinstance(game.player, Player)
    assert game.player.money == 100000
    assert game.player.reputation == 50
    assert len(game.player.vineyards) == 1
    assert game.player.vineyards[0].name == "Home Block"
    assert game.player.winery is not None
    assert len(game.player.winery.vessels) == 5
    assert game.current_year == 2025
    assert game.current_month_index == 0

def test_advance_month_within_year():
    game = Game()
    initial_month = game.current_month_index
    initial_year = game.current_year
    game.advance_month()
    assert game.current_month_index == initial_month + 1
    assert game.current_year == initial_year

def test_advance_month_new_year():
    game = Game()
    game.current_month_index = 11  # Set to December
    initial_year = game.current_year
    game.advance_month()
    assert game.current_month_index == 0
    assert game.current_year == initial_year + 1
    assert not game.player.vineyards[0].harvested_this_year
    assert not game.player.vineyards[0].grapes_ready

def test_buy_vineyard_success():
    game = Game()
    initial_money = game.player.money
    initial_reputation = game.player.reputation
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game.buy_vineyard(vineyard_data, "Jura Savagnin")
    assert new_vineyard is not None
    assert new_vineyard.name == "Jura Savagnin"
    assert game.player.money < initial_money
    assert game.player.reputation == initial_reputation + 2
    assert new_vineyard in game.player.vineyards

def test_buy_vineyard_not_enough_money():
    game = Game()
    game.player.money = 10000 # Set low money
    vineyard_data = {"region": "Jura", "varietal": "Savagnin", "cost": 40000}
    new_vineyard = game.buy_vineyard(vineyard_data, "Jura Savagnin")
    assert new_vineyard is None
    assert len(game.player.vineyards) == 1 # Still only the initial vineyard

def test_tend_vineyard_success():
    game = Game()
    vineyard = game.player.vineyards[0]
    initial_health = vineyard.health
    initial_money = game.player.money
    success = game.tend_vineyard(vineyard.name)
    assert success
    assert vineyard.health > initial_health
    assert game.player.money == initial_money - 500

def test_tend_vineyard_not_enough_money():
    game = Game()
    game.player.money = 100 # Not enough to tend
    vineyard = game.player.vineyards[0]
    initial_health = vineyard.health
    success = game.tend_vineyard(vineyard.name)
    assert not success
    assert vineyard.health == initial_health

def test_harvest_grapes_success():
    game = Game()
    vineyard = game.player.vineyards[0]
    vineyard.grapes_ready = True
    initial_grapes_count = len(game.player.grapes_inventory)
    initial_reputation = game.player.reputation
    harvested_grapes = game.harvest_grapes(vineyard.name)
    assert harvested_grapes is not None
    assert harvested_grapes.varietal == vineyard.varietal
    assert harvested_grapes.vintage == game.current_year
    assert len(game.player.grapes_inventory) == initial_grapes_count + 1
    assert vineyard.harvested_this_year
    assert not vineyard.grapes_ready
    assert game.player.reputation == initial_reputation + 5

def test_harvest_grapes_not_ready():
    game = Game()
    vineyard = game.player.vineyards[0]
    vineyard.grapes_ready = False # Not ready
    harvested_grapes = game.harvest_grapes(vineyard.name)
    assert harvested_grapes is None

def test_buy_vessel_success():
    game = Game()
    initial_vessel_count = len(game.player.winery.vessels)
    initial_money = game.player.money
    new_vessel = game.buy_vessel("Concrete Egg")
    assert new_vessel is not None
    assert new_vessel.type == "Concrete Egg"
    assert len(game.player.winery.vessels) == initial_vessel_count + 1
    assert game.player.money < initial_money

def test_buy_vessel_not_enough_money():
    game = Game()
    game.player.money = 100 # Not enough
    new_vessel = game.buy_vessel("Concrete Egg")
    assert new_vessel is None

def test_process_grapes_success():
    game = Game()
    # Add some grapes to inventory for testing
    game.player.grapes_inventory.append(Grape(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70))
    initial_grapes_count = len(game.player.grapes_inventory)
    initial_must_count = len(game.player.winery.must_in_production)

    processed_must = game.process_grapes(0, "yes", "Destemmed/Crushed")
    assert processed_must is not None
    assert processed_must.varietal == "Pinot Noir"
    assert len(game.player.grapes_inventory) == initial_grapes_count - 1
    assert len(game.player.winery.must_in_production) == initial_must_count + 1
    assert processed_must.processing_method == "Sorted"

def test_start_fermentation_success():
    game = Game()
    # Add must and ensure a vessel is available
    game.player.winery.must_in_production.append(Must(varietal="Pinot Noir", vintage=2025, quantity_kg=500, quality=70, processing_method="Sorted", destem_crush_method="Destemmed/Crushed"))
    game.player.winery.vessels.append(WineryVessel(type="Stainless Steel Tank", capacity=1000, in_use=False))

    initial_must_count = len(game.player.winery.must_in_production)
    initial_fermenting_count = len(game.player.winery.wines_fermenting)
    initial_reputation = game.player.reputation

    wine_in_prod = game.start_fermentation(0, 5) # must_index 0, vessel_index 5 (the new one)
    assert wine_in_prod is not None
    assert wine_in_prod.varietal == "Pinot Noir"
    assert wine_in_prod.stage == "fermenting"
    assert len(game.player.winery.must_in_production) == initial_must_count - 1
    assert len(game.player.winery.wines_fermenting) == initial_fermenting_count + 1
    assert game.player.winery.vessels[5].in_use
    assert game.player.reputation == initial_reputation + 3

def test_perform_maceration_action_success():
    game = Game()
    # Add a red wine in fermentation
    game.player.winery.wines_fermenting.append(WineInProduction(varietal="Pinot Noir", vintage=2025, quantity_liters=300, quality=70, vessel_type="Open Top Fermenter", vessel_index=1, stage="fermenting"))
    initial_quality = game.player.winery.wines_fermenting[0].quality
    success = game.perform_maceration_action(0, "punch_down")
    assert success
    assert game.player.winery.wines_fermenting[0].quality > initial_quality
    assert game.player.winery.wines_fermenting[0].maceration_actions_taken == 1

def test_start_aging_success():
    game = Game()
    # Add a fermented wine and an aging vessel
    game.player.winery.wines_fermenting.append(WineInProduction(varietal="Chardonnay", vintage=2025, quantity_liters=200, quality=80, vessel_type="Stainless Steel Tank", vessel_index=0, stage="fermenting", fermentation_progress=100))
    game.player.winery.vessels.append(WineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False))

    initial_fermenting_count = len(game.player.winery.wines_fermenting)
    initial_aging_count = len(game.player.winery.wines_aging)

    wine_in_prod = game.start_aging(0, 5, 6) # wine_prod_index 0, vessel_index 5 (the new one), 6 months aging
    assert wine_in_prod is not None
    assert wine_in_prod.stage == "aging"
    assert wine_in_prod.aging_duration == 6
    assert len(game.player.winery.wines_fermenting) == initial_fermenting_count - 1
    assert len(game.player.winery.wines_aging) == initial_aging_count + 1
    assert game.player.winery.vessels[5].in_use

def test_bottle_wine_success():
    game = Game()
    # Add an aged wine
    game.player.winery.wines_aging.append(WineInProduction(varietal="Chardonnay", vintage=2024, quantity_liters=750, quality=85, vessel_type="Neutral Oak Barrel (225L)", vessel_index=2, stage="aging", aging_progress=12, aging_duration=12))

    initial_aging_count = len(game.player.winery.wines_aging)
    initial_bottled_count = len(game.player.bottled_wines)
    initial_reputation = game.player.reputation

    bottled_wine = game.bottle_wine(0, "My Great Chardonnay")
    assert bottled_wine is not None
    assert bottled_wine.name == "My Great Chardonnay"
    assert bottled_wine.bottles == 1000 # 750L / 0.75L per bottle
    assert len(game.player.winery.wines_aging) == initial_aging_count - 1
    assert len(game.player.bottled_wines) == initial_bottled_count + 1
    assert not game.player.winery.vessels[2].in_use
    assert game.player.reputation == initial_reputation + 10