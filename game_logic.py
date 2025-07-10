import random
from typing import List, Dict, Any, Optional
from game_models import Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, WineryVessel

# --- Game Data ---
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
    def __init__(self):
        self.player = Player()
        self.current_year = 2025
        self.current_month_index = 0 # 0 = January, 11 = December
        self.months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        self.game_running = True

        # Initial setup: Give the player a starting vineyard and winery
        starting_vineyard = Vineyard(name="Home Block", varietal="Pinot Noir", region="Willamette Valley", size_acres=5)
        self.player.vineyards.append(starting_vineyard)
        
        initial_vessels = [
            WineryVessel(type="Stainless Steel Tank", capacity=5000, in_use=False),
            WineryVessel(type="Open Top Fermenter", capacity=1000, in_use=False),
            WineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
            WineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
            WineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
        ]
        self.player.winery = Winery(vessels=initial_vessels)

    def advance_month(self):
        self.current_month_index += 1
        if self.current_month_index >= len(self.months):
            self.current_month_index = 0
            self.current_year += 1
            # Reset for new year
            for vineyard in self.player.vineyards:
                vineyard.harvested_this_year = False
                vineyard.grapes_ready = False # Will be set to True again when ripe

        # Monthly updates for vineyards
        current_month_num = self.current_month_index + 1 # 1-indexed for comparison with ripening_month
        for vineyard in self.player.vineyards:
            # Health decay if not tended
            if random.random() < 0.2: # 20% chance of health decay each month
                vineyard.health = max(0, vineyard.health - random.randint(1, 3))

            # Check for grape ripening
            ripening_month = GRAPE_CHARACTERISTICS[vineyard.varietal]["ripening_month"]
            if current_month_num == ripening_month and not vineyard.harvested_this_year:
                vineyard.grapes_ready = True

        # Monthly updates for winery production
        for wine_prod in list(self.player.winery.wines_fermenting): # Iterate over a copy to allow modification
            if wine_prod.fermentation_progress < 100:
                # Simulate fermentation progress (faster for smaller batches, higher quality grapes)
                progress_gain = random.randint(10, 25) + int(wine_prod.quality / 10)
                wine_prod.fermentation_progress = min(100, wine_prod.fermentation_progress + progress_gain)
                # if wine_prod.fermentation_progress >= 100:
                    # messagebox.showinfo("Game Event", f"Fermentation complete for {wine_prod.varietal} (Vintage {wine_prod.vintage})!")
                    # No automatic move to aging, player must choose

        for wine_prod in list(self.player.winery.wines_aging): # Iterate over a copy
            if wine_prod.aging_progress < wine_prod.aging_duration:
                wine_prod.aging_progress += 1
                # if wine_prod.aging_progress >= wine_prod.aging_duration:
                    # messagebox.showinfo("Game Event", f"Aging complete for {wine_prod.varietal} (Vintage {wine_prod.vintage})!")
                    # No automatic move to bottling, player must choose

    def buy_vineyard(self, vineyard_data: Dict[str, Any], vineyard_name: str) -> Optional[Vineyard]:
        cost = vineyard_data["cost"]
        print(f"[game_logic] Player money before purchase: {self.player.money}")
        print(f"[game_logic] Vineyard cost: {cost}")
        if self.player.money >= cost:
            new_vineyard = Vineyard(
                name=vineyard_name,
                varietal=vineyard_data["varietal"],
                region=vineyard_data["region"],
                size_acres=random.randint(3, 10),
                age_of_vines=random.randint(3, 20),
                soil_type=random.choice(REGIONS[vineyard_data["region"]]["soil_types"])
            )
            self.player.vineyards.append(new_vineyard)
            self.player.money -= cost
            self.player.reputation += 2
            print(f"[game_logic] Player money after successful purchase: {self.player.money}")
            print(f"[game_logic] Returning new vineyard: {new_vineyard.name}")
            return new_vineyard
        print(f"[game_logic] Not enough money. Returning None.")
        return None

    def tend_vineyard(self, vineyard_name: str) -> bool:
        cost = 500
        if self.player.money >= cost:
            for vineyard in self.player.vineyards:
                if vineyard.name == vineyard_name:
                    self.player.money -= cost
                    vineyard.health = min(100, vineyard.health + random.randint(5, 15))
                    return True
        return False

    def harvest_grapes(self, vineyard_name: str) -> Optional[Grape]:
        for vineyard in self.player.vineyards:
            if vineyard.name == vineyard_name and vineyard.grapes_ready and not vineyard.harvested_this_year:
                base_yield_per_acre = 1000 # kg
                yield_kg = int(base_yield_per_acre * vineyard.size_acres * (vineyard.health / 100.0) * random.uniform(0.8, 1.2))

                base_quality = GRAPE_CHARACTERISTICS[vineyard.varietal]["base_quality"]
                grape_quality = int(base_quality * (vineyard.health / 100.0) + random.randint(-5, 5))
                grape_quality = max(1, min(100, grape_quality))

                new_grapes = Grape(
                    varietal=vineyard.varietal,
                    vintage=self.current_year,
                    quantity_kg=yield_kg,
                    quality=grape_quality
                )
                self.player.grapes_inventory.append(new_grapes)
                vineyard.harvested_this_year = True
                vineyard.grapes_ready = False
                self.player.reputation += 5
                return new_grapes
        return None

    def buy_vessel(self, vessel_type_name: str) -> Optional[WineryVessel]:
        if vessel_type_name in VESSEL_TYPES:
            vessel_data = VESSEL_TYPES[vessel_type_name]
            cost = vessel_data["cost"]
            if self.player.money >= cost:
                new_vessel = WineryVessel(type=vessel_type_name, capacity=vessel_data["capacity"], in_use=False)
                self.player.winery.vessels.append(new_vessel)
                self.player.money -= cost
                return new_vessel
        return None

    def process_grapes(self, grape_index: int, sort_choice: str, destem_crush_method: str) -> Optional[Must]:
        if 0 <= grape_index < len(self.player.grapes_inventory):
            selected_grapes = self.player.grapes_inventory[grape_index]
            initial_quality = selected_grapes.quality
            processing_method = "Unsorted"

            # Sorting logic
            if sort_choice == "yes":
                sort_cost = (selected_grapes.quantity_kg / 100) * 100
                if self.player.money >= sort_cost:
                    self.player.money -= sort_cost
                    selected_grapes.quality = min(100, selected_grapes.quality + random.randint(2, 5))
                    processing_method = "Sorted"
                # else: not enough money, processed unsorted
            else:
                selected_grapes.quality = max(1, selected_grapes.quality - random.randint(1, 3))

            # Destemming/Crushing logic
            if destem_crush_method == "Whole Cluster":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(-2, 4))
            elif destem_crush_method == "Partial Destem":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(0, 2))
            elif destem_crush_method == "Destemmed/Crushed":
                selected_grapes.quality = max(1, selected_grapes.quality + random.randint(-1, 1))

            new_must = Must(
                varietal=selected_grapes.varietal,
                vintage=self.current_year,
                quantity_kg=selected_grapes.quantity_kg,
                quality=selected_grapes.quality,
                processing_method=processing_method,
                destem_crush_method=destem_crush_method
            )
            self.player.winery.must_in_production.append(new_must)
            self.player.grapes_inventory.pop(grape_index) # Remove processed grapes
            return new_must
        return None

    def start_fermentation(self, must_index: int, vessel_index: int) -> Optional[WineInProduction]:
        if 0 <= must_index < len(self.player.winery.must_in_production) and \
           0 <= vessel_index < len(self.player.winery.vessels):
            must = self.player.winery.must_in_production[must_index]
            vessel = self.player.winery.vessels[vessel_index]

            if not vessel.in_use and vessel.capacity >= must.quantity_kg * 0.75 and \
               ("fermentation" in VESSEL_TYPES[vessel.type]["type"]):
                
                vessel.in_use = True
                quantity_liters = must.quantity_kg * 0.75

                new_wine_in_prod = WineInProduction(
                    varietal=must.varietal,
                    vintage=self.current_year,
                    quantity_liters=quantity_liters,
                    quality=must.quality,
                    vessel_type=vessel.type,
                    vessel_index=vessel_index,
                    stage="fermenting"
                )
                self.player.winery.wines_fermenting.append(new_wine_in_prod)
                self.player.winery.must_in_production.pop(must_index)
                self.player.reputation += 3
                return new_wine_in_prod
        return None

    def perform_maceration_action(self, wine_prod_index: int, action_type: str) -> bool:
        if 0 <= wine_prod_index < len(self.player.winery.wines_fermenting):
            wine_prod = self.player.winery.wines_fermenting[wine_prod_index]
            if GRAPE_CHARACTERISTICS[wine_prod.varietal]["color"] == "red":
                wine_prod.quality = min(100, wine_prod.quality + random.randint(1, 3))
                wine_prod.maceration_actions_taken += 1
                return True
        return False

    def start_aging(self, wine_prod_index: int, vessel_index: int, aging_duration: int) -> Optional[WineInProduction]:
        if 0 <= wine_prod_index < len(self.player.winery.wines_fermenting) and \
           0 <= vessel_index < len(self.player.winery.vessels):
            wine_prod = self.player.winery.wines_fermenting[wine_prod_index]
            vessel = self.player.winery.vessels[vessel_index]

            if wine_prod.fermentation_progress >= 100 and not vessel.in_use and \
               vessel.capacity >= wine_prod.quantity_liters and ("aging" in VESSEL_TYPES[vessel.type]["type"]):
                
                vessel.in_use = True
                wine_prod.vessel_type = vessel.type
                wine_prod.vessel_index = vessel_index
                wine_prod.stage = "aging"
                wine_prod.aging_duration = aging_duration
                self.player.winery.wines_aging.append(wine_prod)
                self.player.winery.wines_fermenting.pop(wine_prod_index)
                return wine_prod
        return None

    def bottle_wine(self, wine_prod_index: int, wine_name: str) -> Optional[Wine]:
        if 0 <= wine_prod_index < len(self.player.winery.wines_aging):
            selected_wine_prod = self.player.winery.wines_aging[wine_prod_index]

            if selected_wine_prod.aging_progress >= selected_wine_prod.aging_duration:
                bottles_produced = int(selected_wine_prod.quantity_liters / 0.75)

                new_bottled_wine = Wine(
                    name=wine_name,
                    vintage=selected_wine_prod.vintage,
                    varietal=selected_wine_prod.varietal,
                    style=GRAPE_CHARACTERISTICS[selected_wine_prod.varietal]["color"].capitalize(),
                    quality=selected_wine_prod.quality,
                    bottles=bottles_produced
                )
                self.player.bottled_wines.append(new_bottled_wine)
                self.player.winery.vessels[selected_wine_prod.vessel_index].in_use = False
                self.player.winery.wines_aging.pop(wine_prod_index)
                self.player.reputation += 10
                return new_bottled_wine
        return None

    def get_available_vineyards_for_purchase(self) -> List[Dict[str, Any]]:
        available_vineyards = []
        for region_name, region_data in REGIONS.items():
            for varietal in region_data["grape_varietals"]:
                cost = region_data["base_cost"] + random.randint(-5000, 5000)
                available_vineyards.append({"region": region_name, "varietal": varietal, "cost": cost})
        return available_vineyards

    def get_available_vessel_types_for_purchase(self) -> List[Dict[str, Any]]:
        available_vessel_types = []
        for vessel_name, data in VESSEL_TYPES.items():
            available_vessel_types.append({"name": vessel_name, "capacity": data["capacity"], "cost": data["cost"], "type": data["type"]})
        return available_vessel_types
