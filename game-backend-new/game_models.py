from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, VARCHAR
import json

Base = declarative_base()

# Custom type for JSON storage
class JSONEncodedDict(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

# SQLAlchemy ORM Models
class DBGrapeCharacteristics(Base):
    __tablename__ = "grape_characteristics"
    id = Column(Integer, primary_key=True, index=True)
    color = Column(String)
    ripening_month = Column(Integer)
    base_quality = Column(Integer)

class DBRegionData(Base):
    __tablename__ = "region_data"
    id = Column(Integer, primary_key=True, index=True)
    climate = Column(String)
    soil_types = Column(JSONEncodedDict) # Storing as JSON string
    grape_varietals = Column(JSONEncodedDict) # Storing as JSON string
    base_cost = Column(Integer)

class DBVesselTypeData(Base):
    __tablename__ = "vessel_type_data"
    id = Column(Integer, primary_key=True, index=True)
    capacity = Column(Integer)
    cost = Column(Integer)
    type = Column(String)

class DBGrape(Base):
    __tablename__ = "grapes"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    varietal = Column(String)
    vintage = Column(Integer)
    quantity_kg = Column(Float)
    quality = Column(Integer)

class DBMust(Base):
    __tablename__ = "musts"
    id = Column(Integer, primary_key=True, index=True)
    winery_id = Column(Integer, ForeignKey("wineries.id"))
    varietal = Column(String)
    vintage = Column(Integer)
    quantity_kg = Column(Float)
    quality = Column(Integer)
    processing_method = Column(String)
    destem_crush_method = Column(String)
    fermented = Column(Boolean, default=False)

class DBWineInProduction(Base):
    __tablename__ = "wines_in_production"
    id = Column(Integer, primary_key=True, index=True)
    winery_id = Column(Integer, ForeignKey("wineries.id"))
    varietal = Column(String)
    vintage = Column(Integer)
    quantity_liters = Column(Float)
    quality = Column(Integer)
    vessel_type = Column(String)
    vessel_index = Column(Integer)
    stage = Column(String)
    fermentation_progress = Column(Integer, default=0)
    aging_progress = Column(Integer, default=0)
    aging_duration = Column(Integer, default=0)
    maceration_actions_taken = Column(Integer, default=0)

class DBWine(Base):
    __tablename__ = "wines"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    name = Column(String)
    vintage = Column(Integer)
    varietal = Column(String)
    style = Column(String)
    quality = Column(Integer)
    bottles = Column(Integer)

class DBVineyard(Base):
    __tablename__ = "vineyards"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    name = Column(String, unique=True, index=True)
    varietal = Column(String)
    region = Column(String)
    size_acres = Column(Integer, default=5)
    age_of_vines = Column(Integer, default=5)
    soil_type = Column(String, default="mixed")
    health = Column(Integer, default=80)
    grapes_ready = Column(Boolean, default=False)
    harvested_this_year = Column(Boolean, default=False)

class DBWineryVessel(Base):
    __tablename__ = "winery_vessels"
    id = Column(Integer, primary_key=True, index=True)
    winery_id = Column(Integer, ForeignKey("wineries.id"))
    type = Column(String)
    capacity = Column(Integer)
    in_use = Column(Boolean, default=False)

class DBWinery(Base):
    __tablename__ = "wineries"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    name = Column(String, default="Main Winery")
    vessels = relationship("DBWineryVessel", backref="winery", cascade="all, delete-orphan")
    must_in_production = relationship("DBMust", backref="winery", cascade="all, delete-orphan")
    wines_fermenting = relationship("DBWineInProduction", primaryjoin="and_(DBWineInProduction.winery_id==DBWinery.id, DBWineInProduction.stage=='fermenting')", backref="fermenting_winery", cascade="all, delete-orphan")
    wines_aging = relationship("DBWineInProduction", primaryjoin="and_(DBWineInProduction.winery_id==DBWinery.id, DBWineInProduction.stage=='aging')", backref="aging_winery", cascade="all, delete-orphan")

class DBPlayer(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Winemaker")
    money = Column(Float, default=100000)
    reputation = Column(Integer, default=50)
    vineyards = relationship("DBVineyard", backref="player", cascade="all, delete-orphan")
    winery = relationship("DBWinery", uselist=False, backref="player", cascade="all, delete-orphan")
    grapes_inventory = relationship("DBGrape", backref="player", cascade="all, delete-orphan")
    bottled_wines = relationship("DBWine", backref="player", cascade="all, delete-orphan")

class DBGameState(Base):
    __tablename__ = "game_state"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    player = relationship("DBPlayer", uselist=False, backref="game_state", cascade="all, delete-orphan")
    current_year = Column(Integer)
    current_month_index = Column(Integer)
    months = Column(JSONEncodedDict) # Storing as JSON string

# Pydantic Models (for API request/response validation)
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
    id: Optional[int] = None
    varietal: str
    vintage: int
    quantity_kg: float
    quality: int

class Must(BaseModel):
    id: Optional[int] = None
    varietal: str
    vintage: int
    quantity_kg: float
    quality: int
    processing_method: str
    destem_crush_method: str
    fermented: bool = False

class WineInProduction(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None
    name: str
    vintage: int
    varietal: str
    style: str
    quality: int
    bottles: int

class Vineyard(BaseModel):
    id: Optional[int] = None
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
    id: Optional[int] = None
    type: str
    capacity: int
    in_use: bool = False

class Winery(BaseModel):
    id: Optional[int] = None
    name: str = "Main Winery"
    vessels: List[WineryVessel] = []
    must_in_production: List[Must] = []
    wines_fermenting: List[WineInProduction] = []
    wines_aging: List[WineInProduction] = []

class Player(BaseModel):
    id: Optional[int] = None
    name: str = "Winemaker"
    money: float = 100000
    reputation: int = 50
    vineyards: List[Vineyard] = []
    winery: Optional[Winery] = None
    grapes_inventory: List[Grape] = []
    bottled_wines: List[Wine] = []

class GameState(BaseModel):
    id: Optional[int] = None
    player: Player
    current_year: int
    current_month_index: int
    months: List[str]
    event_message: Optional[str] = None

# Request Body Models
class BuyVineyardRequest(BaseModel):
    region: str
    varietal: str
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

class BuyVineyardResponse(BaseModel):
    new_vineyard: Vineyard
    updated_money: float

class SellWineRequest(BaseModel):
    wine_id: int
    bottles: int

class SellWineResponse(BaseModel):
    updated_money: float
    sold_wine_id: int
    bottles_remaining: int