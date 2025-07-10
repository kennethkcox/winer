import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from game_models import (
    GrapeCharacteristics, RegionData, VesselTypeData,
    Grape, Must, WineInProduction, Wine, Vineyard, WineryVessel, Winery, Player, GameState,
    DBGrapeCharacteristics, DBRegionData, DBVesselTypeData,
    DBGrape, DBMust, DBWineInProduction, DBWine, DBVineyard, DBWineryVessel, DBWinery, DBPlayer, DBGameState
)
from database import SessionLocal, engine, Base
import logging

logger = logging.getLogger(__name__)

# --- Game Data (Constants) ---
REGIONS = {
    "Willamette Valley": {
        "climate": "cool",
        "soil_types": ["volcanic", "sedimentary"],
        "grape_varietals": ["Pinot Noir", "Chardonnay", "Pinot Gris"],
        "base_cost": 50000
    },
    "Jura": {
        "climate": "cool",
        "soil_types": ["marl", "limestone"],
        "grape_varietals": ["Savagnin", "Poulsard", "Trousseau", "Chardonnay", "Pinot Noir"],
        "base_cost": 40000
    },
    "Northern Rhône": {
        "climate": "continental",
        "soil_types": ["granite", "schist"],
        "grape_varietals": ["Syrah", "Viognier"],
        "base_cost": 60000
    }
}

GRAPE_CHARACTERISTICS = {
    "Pinot Noir": {"color": "red", "ripening_month": 9, "base_quality": 70},
    "Chardonnay": {"color": "white", "ripening_month": 9, "base_quality": 65},
    "Pinot Gris": {"color": "white", "ripening_month": 9, "base_quality": 60},
    "Savagnin": {"color": "white", "ripening_month": 10, "base_quality": 75},
    "Poulsard": {"color": "red", "ripening_month": 9, "base_quality": 68},
    "Trousseau": {"color": "red", "ripening_month": 9, "base_quality": 68},
    "Syrah": {"color": "red", "ripening_month": 9, "base_quality": 72},
    "Viognier": {"color": "white", "ripening_month": 9, "base_quality": 70},
}

VESSEL_TYPES = {
    "Stainless Steel Tank": {"capacity": 5000, "cost": 10000, "type": "fermentation/aging"},
    "Open Top Fermenter": {"capacity": 1000, "cost": 2000, "type": "fermentation"},
    "Neutral Oak Barrel (225L)": {"capacity": 225, "cost": 500, "type": "aging"},
    "Concrete Egg": {"capacity": 1500, "cost": 7000, "type": "fermentation/aging"},
    "Amphora (500L)": {"capacity": 500, "cost": 3000, "type": "fermentation/aging"}
}

class Game:
    def __init__(self, db: Session):
        self.db = db
        Base.metadata.create_all(bind=engine) # Create tables if they don't exist
        self._initialize_game_state_if_empty()

    def _initialize_game_state_if_empty(self):
        game_state = self.db.query(DBGameState).first()
        if not game_state:
            logger.info("Initializing new game state.")
            # Create initial player
            player = DBPlayer(name="Winemaker", money=100000, reputation=50)
            self.db.add(player)
            self.db.flush() # Flush to get player.id

            # Create initial winery
            initial_vessels = [
                DBWineryVessel(type="Stainless Steel Tank", capacity=5000, in_use=False),
                DBWineryVessel(type="Open Top Fermenter", capacity=1000, in_use=False),
                DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
                DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
                DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
            ]
            winery = DBWinery(name="Main Winery", player_id=player.id, vessels=initial_vessels)
            self.db.add(winery)
            self.db.flush() # Flush to get winery.id
            player.winery = winery # Link winery to player

            # Create initial vineyard
            starting_vineyard = DBVineyard(name="Home Block", varietal="Pinot Noir", region="Willamette Valley", size_acres=5, player_id=player.id)
            self.db.add(starting_vineyard)

            # Create initial game state
            months_list = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            game_state = DBGameState(player_id=player.id, current_year=2025, current_month_index=0, months=months_list)
            self.db.add(game_state)
            self.db.commit()
            self.db.refresh(player)
            self.db.refresh(game_state)
            logger.info("Game state initialized successfully.")
        else:
            logger.info("Game state already exists. Loading existing game.")

    def get_game_state(self) -> GameState:
        db_game_state = self.db.query(DBGameState).first()
        if not db_game_state:
            logger.error("Game state not found during retrieval. This indicates an initialization issue.")
            raise Exception("Game state not found. This should not happen after initialization.")
        return GameState.model_validate(db_game_state)

    def advance_month(self):
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()

        db_game_state.current_month_index += 1
        if db_game_state.current_month_index >= len(db_game_state.months):
            db_game_state.current_month_index = 0
            db_game_state.current_year += 1
            logger.info(f"New year: {db_game_state.current_year}. Resetting vineyard harvest status.")
            # Reset for new year
            for vineyard in db_player.vineyards:
                vineyard.harvested_this_year = False
                vineyard.grapes_ready = False # Will be set to True again when ripe

        # Monthly updates for vineyards
        current_month_num = db_game_state.current_month_index + 1 # 1-indexed for comparison with ripening_month
        for vineyard in db_player.vineyards:
            # Health decay if not tended
            if random.random() < 0.2: # 20% chance of health decay each month
                vineyard.health = max(0, vineyard.health - random.randint(1, 3))
                logger.debug(f"Vineyard {vineyard.name} health decayed to {vineyard.health}.")

            # Check for grape ripening
            ripening_month = GRAPE_CHARACTERISTICS[vineyard.varietal]["ripening_month"]
            if current_month_num == ripening_month and not vineyard.harvested_this_year:
                vineyard.grapes_ready = True
                logger.info(f"Grapes in {vineyard.name} ({vineyard.varietal}) are now ready for harvest.")

        # Monthly updates for winery production
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()
        if db_winery:
            for wine_prod in list(db_winery.wines_fermenting): # Iterate over a copy to allow modification
                if wine_prod.fermentation_progress < 100:
                    # Simulate fermentation progress (faster for smaller batches, higher quality grapes)
                    progress_gain = random.randint(10, 25) + int(wine_prod.quality / 10)
                    wine_prod.fermentation_progress = min(100, wine_prod.fermentation_progress + progress_gain)
                    logger.debug(f"Fermentation progress for {wine_prod.varietal}: {wine_prod.fermentation_progress}%")

            for wine_prod in list(db_winery.wines_aging): # Iterate over a copy
                if wine_prod.aging_progress < wine_prod.aging_duration:
                    wine_prod.aging_progress += 1
                    logger.debug(f"Aging progress for {wine_prod.varietal}: {wine_prod.aging_progress}/{wine_prod.aging_duration} months.")
        
        self.db.commit()
        self.db.refresh(db_game_state)
        self.db.refresh(db_player)
        logger.info(f"Advanced to {db_game_state.months[db_game_state.current_month_index]}, {db_game_state.current_year}.")

    def buy_vineyard(self, vineyard_data: Dict[str, Any], vineyard_name: str) -> Optional[Vineyard]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()

        cost = vineyard_data["cost"]
        logger.info(f"Attempting to buy vineyard '{vineyard_name}' for ${cost}. Player money: ${db_player.money}")
        if db_player.money >= cost:
            new_vineyard = DBVineyard(
                name=vineyard_name,
                varietal=vineyard_data["varietal"],
                region=vineyard_data["region"],
                size_acres=random.randint(3, 10),
                age_of_vines=random.randint(3, 20),
                soil_type=random.choice(REGIONS[vineyard_data["region"]]["soil_types"]),
                player_id=db_player.id
            )
            self.db.add(new_vineyard)
            db_player.money -= cost
            db_player.reputation += 2
            self.db.commit()
            self.db.refresh(new_vineyard)
            self.db.refresh(db_player)
            logger.info(f"Successfully purchased vineyard '{vineyard_name}'. New money: ${db_player.money}")
            return Vineyard.model_validate(new_vineyard)
        logger.warning(f"Failed to buy vineyard '{vineyard_name}': Not enough money.")
        return None

    def tend_vineyard(self, vineyard_name: str) -> bool:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()

        cost = 500
        logger.info(f"Attempting to tend vineyard '{vineyard_name}' for ${cost}. Player money: ${db_player.money}")
        if db_player.money >= cost:
            vineyard = self.db.query(DBVineyard).filter(DBVineyard.player_id == db_player.id, DBVineyard.name == vineyard_name).first()
            if vineyard:
                db_player.money -= cost
                vineyard.health = min(100, vineyard.health + random.randint(5, 15))
                self.db.commit()
                self.db.refresh(db_player)
                self.db.refresh(vineyard)
                logger.info(f"Successfully tended vineyard '{vineyard_name}'. New health: {vineyard.health}")
                return True
            logger.warning(f"Failed to tend vineyard '{vineyard_name}': Vineyard not found.")
        else:
            logger.warning(f"Failed to tend vineyard '{vineyard_name}': Not enough money.")
        return False

    def harvest_grapes(self, vineyard_name: str) -> Optional[Grape]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()

        vineyard = self.db.query(DBVineyard).filter(DBVineyard.player_id == db_player.id, DBVineyard.name == vineyard_name).first()
        logger.info(f"Attempting to harvest grapes from '{vineyard_name}'. Grapes ready: {vineyard.grapes_ready}, Harvested this year: {vineyard.harvested_this_year}")
        if vineyard and vineyard.grapes_ready and not vineyard.harvested_this_year:
            base_yield_per_acre = 1000 # kg
            yield_kg = int(base_yield_per_acre * vineyard.size_acres * (vineyard.health / 100.0) * random.uniform(0.8, 1.2))

            base_quality = GRAPE_CHARACTERISTICS[vineyard.varietal]["base_quality"]
            grape_quality = int(base_quality * (vineyard.health / 100.0) + random.randint(-5, 5))
            grape_quality = max(1, min(100, grape_quality))

            new_grapes = DBGrape(
                varietal=vineyard.varietal,
                vintage=db_game_state.current_year,
                quantity_kg=yield_kg,
                quality=grape_quality,
                player_id=db_player.id
            )
            self.db.add(new_grapes)
            vineyard.harvested_this_year = True
            vineyard.grapes_ready = False
            db_player.reputation += 5
            self.db.commit()
            self.db.refresh(new_grapes)
            self.db.refresh(vineyard)
            self.db.refresh(db_player)
            logger.info(f"Successfully harvested {yield_kg}kg of {vineyard.varietal} grapes from '{vineyard_name}'. Quality: {grape_quality}")
            return Grape.model_validate(new_grapes)
        logger.warning(f"Failed to harvest grapes from '{vineyard_name}': Grapes not ready or already harvested.")
        return None

    def buy_vessel(self, vessel_type_name: str) -> Optional[WineryVessel]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        logger.info(f"Attempting to buy vessel of type '{vessel_type_name}'. Player money: ${db_player.money}")
        if vessel_type_name in VESSEL_TYPES:
            vessel_data = VESSEL_TYPES[vessel_type_name]
            cost = vessel_data["cost"]
            if db_player.money >= cost:
                new_vessel = DBWineryVessel(type=vessel_type_name, capacity=vessel_data["capacity"], in_use=False, winery_id=db_winery.id)
                self.db.add(new_vessel)
                db_player.money -= cost
                self.db.commit()
                self.db.refresh(new_vessel)
                self.db.refresh(db_player)
                logger.info(f"Successfully purchased vessel '{vessel_type_name}'. New money: ${db_player.money}")
                return WineryVessel.model_validate(new_vessel)
            logger.warning(f"Failed to buy vessel '{vessel_type_name}': Not enough money.")
        else:
            logger.warning(f"Failed to buy vessel: Invalid vessel type name '{vessel_type_name}'.")
        return None

    def process_grapes(self, grape_index: int, sort_choice: str, destem_crush_method: str) -> Optional[Must]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        if 0 <= grape_index < len(db_player.grapes_inventory):
            selected_grapes = db_player.grapes_inventory[grape_index]
            logger.info(f"Processing {selected_grapes.quantity_kg}kg of {selected_grapes.varietal} grapes (index {grape_index}). Sort choice: {sort_choice}, Destem/Crush: {destem_crush_method}")
            initial_quality = selected_grapes.quality
            processing_method = "Unsorted"

            # Sorting logic
            if sort_choice == "yes":
                sort_cost = (selected_grapes.quantity_kg / 100) * 100
                if db_player.money >= sort_cost:
                    db_player.money -= sort_cost
                    selected_grapes.quality = min(100, selected_grapes.quality + random.randint(2, 5))
                    processing_method = "Sorted"
                    logger.info(f"Grapes sorted. Quality increased to {selected_grapes.quality}.")
                else:
                    logger.warning(f"Not enough money to sort grapes. Processing unsorted. Required: ${sort_cost}, Available: ${db_player.money}")

            # Destemming/Crushing logic
            if destem_crush_method == "Whole Cluster":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(-2, 4))
            elif destem_crush_method == "Partial Destem":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(0, 2))
            elif destem_crush_method == "Destemmed/Crushed":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(-1, 1))
            logger.info(f"Grapes destemmed/crushed using '{destem_crush_method}'. Final quality: {selected_grapes.quality}.")

            new_must = DBMust(
                varietal=selected_grapes.varietal,
                vintage=db_game_state.current_year,
                quantity_kg=selected_grapes.quantity_kg,
                quality=selected_grapes.quality,
                processing_method=processing_method,
                destem_crush_method=destem_crush_method,
                winery_id=db_winery.id
            )
            self.db.add(new_must)
            self.db.delete(selected_grapes) # Remove processed grapes
            self.db.commit()
            self.db.refresh(new_must)
            self.db.refresh(db_player)
            logger.info(f"Created must from {new_must.varietal} grapes. Quantity: {new_must.quantity_kg}kg.")
            return Must.model_validate(new_must)
        logger.warning(f"Failed to process grapes: Invalid grape index {grape_index}.")
        return None

    def start_fermentation(self, must_index: int, vessel_index: int) -> Optional[WineInProduction]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        if not (0 <= must_index < len(db_winery.must_in_production) and \
                0 <= vessel_index < len(db_winery.vessels)):
            logger.warning(f"Invalid must_index ({must_index}) or vessel_index ({vessel_index}) for starting fermentation.")
            return None

        must = db_winery.must_in_production[must_index]
        vessel = db_winery.vessels[vessel_index]

        logger.info(f"Attempting to start fermentation for {must.varietal} must in {vessel.type} (index {vessel_index}).")
        if not vessel.in_use and vessel.capacity >= must.quantity_kg * 0.75 and \
           ("fermentation" in VESSEL_TYPES[vessel.type]["type"]):
            
            vessel.in_use = True
            quantity_liters = must.quantity_kg * 0.75

            new_wine_in_prod = DBWineInProduction(
                varietal=must.varietal,
                vintage=db_game_state.current_year,
                quantity_liters=quantity_liters,
                quality=must.quality,
                vessel_type=vessel.type,
                vessel_index=vessel_index,
                stage="fermenting",
                winery_id=db_winery.id
            )
            self.db.add(new_wine_in_prod)
            self.db.delete(must)
            db_player.reputation += 3
            self.db.commit()
            self.db.refresh(new_wine_in_prod)
            self.db.refresh(vessel)
            self.db.refresh(db_player)
            logger.info(f"Fermentation started for {new_wine_in_prod.varietal} in {vessel.type}.")
            return WineInProduction.model_validate(new_wine_in_prod)
        logger.warning(f"Failed to start fermentation: Vessel {vessel.type} (index {vessel_index}) not available or unsuitable for fermentation, or capacity too low.")
        return None

    def perform_maceration_action(self, wine_prod_index: int, action_type: str) -> bool:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        if 0 <= wine_prod_index < len(db_winery.wines_fermenting):
            wine_prod = db_winery.wines_fermenting[wine_prod_index]
            logger.info(f"Performing maceration action '{action_type}' on {wine_prod.varietal} (index {wine_prod_index}).")
            if GRAPE_CHARACTERISTICS[wine_prod.varietal]["color"] == "red":
                wine_prod.quality = min(100, wine_prod.quality + random.randint(1, 3))
                wine_prod.maceration_actions_taken += 1
                self.db.commit()
                self.db.refresh(wine_prod)
                logger.info(f"Maceration action '{action_type}' successful. New quality: {wine_prod.quality}.")
                return True
            logger.warning(f"Maceration action '{action_type}' not applicable for white wine {wine_prod.varietal}.")
        else:
            logger.warning(f"Failed to perform maceration action: Invalid wine in production index {wine_prod_index}.")
        return False

    def start_aging(self, wine_prod_index: int, vessel_index: int) -> Optional[WineInProduction]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        if not (0 <= wine_prod_index < len(db_winery.wines_fermenting) and \
                0 <= vessel_index < len(db_winery.vessels)):
            logger.warning(f"Invalid wine_prod_index ({wine_prod_index}) or vessel_index ({vessel_index}) for starting aging.")
            return None

        wine_prod = db_winery.wines_fermenting[wine_prod_index]
        vessel = db_winery.vessels[vessel_index]

        logger.info(f"Attempting to start aging for {wine_prod.varietal} in {vessel.type} (index {vessel_index}).")
        if wine_prod.fermentation_progress >= 100 and not vessel.in_use and \
           vessel.capacity >= wine_prod.quantity_liters and ("aging" in VESSEL_TYPES[vessel.type]["type"]):
            
            vessel.in_use = True
            wine_prod.vessel_type = vessel.type
            wine_prod.vessel_index = vessel_index
            wine_prod.stage = "aging"
            wine_prod.aging_duration = random.randint(6, 24) # Random aging duration
            db_winery.wines_aging.append(wine_prod)
            db_winery.wines_fermenting.pop(wine_prod_index)
            self.db.commit()
            self.db.refresh(wine_prod)
            self.db.refresh(vessel)
            logger.info(f"Aging started for {wine_prod.varietal} in {vessel.type} for {wine_prod.aging_duration} months.")
            return WineInProduction.model_validate(wine_prod)
        logger.warning(f"Failed to start aging: Wine not fermented, vessel not available or unsuitable, or capacity too low.")
        return None

    def bottle_wine(self, wine_prod_index: int, wine_name: str) -> Optional[Wine]:
        db_game_state = self.db.query(DBGameState).first()
        db_player = self.db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
        db_winery = self.db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()

        if 0 <= wine_prod_index < len(db_winery.wines_aging):
            selected_wine_prod = db_winery.wines_aging[wine_prod_index]
            logger.info(f"Attempting to bottle wine '{wine_name}' from {selected_wine_prod.varietal} (index {wine_prod_index}). Aging progress: {selected_wine_prod.aging_progress}/{selected_wine_prod.aging_duration}")

            if selected_wine_prod.aging_progress >= selected_wine_prod.aging_duration:
                bottles_produced = int(selected_wine_prod.quantity_liters / 0.75)

                new_bottled_wine = DBWine(
                    name=wine_name,
                    vintage=selected_wine_prod.vintage,
                    varietal=selected_wine_prod.varietal,
                    style=GRAPE_CHARACTERISTICS[selected_wine_prod.varietal]["color"].capitalize(),
                    quality=selected_wine_prod.quality,
                    bottles=bottles_produced,
                    player_id=db_player.id
                )
                self.db.add(new_bottled_wine)
                db_winery.vessels[selected_wine_prod.vessel_index].in_use = False
                db_winery.wines_aging.pop(wine_prod_index)
                db_player.reputation += 10
                self.db.commit()
                self.db.refresh(new_bottled_wine)
                self.db.refresh(db_player)
                logger.info(f"Successfully bottled {bottles_produced} bottles of '{wine_name}'.")
                return Wine.model_validate(new_bottled_wine)
            logger.warning(f"Failed to bottle wine '{wine_name}': Wine not ready for bottling (aging not complete).")
        else:
            logger.warning(f"Failed to bottle wine: Invalid wine in production index {wine_prod_index}.")
        return None

    def get_available_vineyards_for_purchase(self) -> List[Dict[str, Any]]:
        logger.info("Retrieving available vineyards for purchase.")
        available_vineyards = []
        for region_name, region_data in REGIONS.items():
            for varietal in region_data["grape_varietals"]:
                cost = region_data["base_cost"] + random.randint(-5000, 5000)
                available_vineyards.append({"region": region_name, "varietal": varietal, "cost": cost})
        return available_vineyards

    def get_available_vessel_types_for_purchase(self) -> List[Dict[str, Any]]:
        logger.info("Retrieving available vessel types for purchase.")
        available_vessel_types = []
        for vessel_name, data in VESSEL_TYPES.items():
            available_vessel_types.append({"name": vessel_name, "capacity": data["capacity"], "cost": data["cost"], "type": data["type"]})
        return available_vessel_types
