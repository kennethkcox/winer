from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class GrapeCharacteristics(BaseModel):
    color: str
    ripening_month: int
    base_quality: int

class RegionData(BaseModel):
    climate: str
    soil_types: List[str]
    grape_varietals: List[str]
    base_cost: int

class VesselTypeData(BaseModel):
    capacity: int
    cost: int
    type: str

class Grape(BaseModel):
    varietal: str
    vintage: int
    quantity_kg: float
    quality: int

class Must(BaseModel):
    varietal: str
    vintage: int
    quantity_kg: float
    quality: int
    processing_method: str
    destem_crush_method: str
    fermented: bool = False

class WineInProduction(BaseModel):
    varietal: str
    vintage: int
    quantity_liters: float
    quality: int
    vessel_type: str
    vessel_index: int
    stage: str
    fermentation_progress: int = 0
    aging_progress: int = 0
    aging_duration: int = 0
    maceration_actions_taken: int = 0

class Wine(BaseModel):
    name: str
    vintage: int
    varietal: str
    style: str
    quality: int
    bottles: int


class Vineyard(BaseModel):
    name: str
    varietal: str
    region: str
    size_acres: int = 5
    age_of_vines: int = 5
    soil_type: str = "mixed"
    health: int = 80
    grapes_ready: bool = False
    harvested_this_year: bool = False

class WineryVessel(BaseModel):
    type: str
    capacity: int
    in_use: bool = False

class Winery(BaseModel):
    name: str = "Main Winery"
    vessels: List[WineryVessel] = []
    must_in_production: List[Must] = []
    wines_fermenting: List[WineInProduction] = []
    wines_aging: List[WineInProduction] = []

class Player(BaseModel):
    name: str = "Winemaker"
    money: float = 100000
    reputation: int = 50
    vineyards: List[Vineyard] = []
    winery: Optional[Winery] = None
    grapes_inventory: List[Grape] = []
    bottled_wines: List[Wine] = []

class GameState(BaseModel):
    player: Player
    current_year: int
    current_month_index: int
    months: List[str]

# Request Body Models
class BuyVineyardRequest(BaseModel):
    vineyard_data: Dict[str, Any]
    vineyard_name: str

class TendVineyardRequest(BaseModel):
    vineyard_name: str

class HarvestGrapesRequest(BaseModel):
    vineyard_name: str

class BuyVesselRequest(BaseModel):
    vessel_type_name: str

class ProcessGrapesRequest(BaseModel):
    grape_index: int
    sort_choice: str
    destem_crush_method: str

class StartFermentationRequest(BaseModel):
    must_index: int
    vessel_index: int

class PerformMacerationActionRequest(BaseModel):
    wine_prod_index: int
    action_type: str

class StartAgingRequest(BaseModel):
    wine_prod_index: int
    vessel_index: int
    aging_duration: int

class BottleWineRequest(BaseModel):
    wine_prod_index: int
    wine_name: str
