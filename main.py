from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    BuyVineyardRequest, TendVineyardRequest, HarvestGrapesRequest, BuyVesselRequest,
    ProcessGrapesRequest, StartFermentationRequest, PerformMacerationActionRequest,
    StartAgingRequest, BottleWineRequest
)
from typing import List, Dict, Any

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

game_instance = Game()

@app.get("/", response_model=GameState)
async def read_root():
    return game_instance

@app.post("/advance_month", response_model=GameState)
async def advance_month():
    game_instance.advance_month()
    return game_instance

@app.get("/player", response_model=Player)
async def get_player():
    return game_instance.player

@app.get("/vineyards", response_model=List[Vineyard])
async def get_vineyards():
    return game_instance.player.vineyards

@app.get("/winery", response_model=Winery)
async def get_winery():
    return game_instance.player.winery

@app.get("/grapes_inventory", response_model=List[Grape])
async def get_grapes_inventory():
    return game_instance.player.grapes_inventory

@app.get("/bottled_wines", response_model=List[Wine])
async def get_bottled_wines():
    return game_instance.player.bottled_wines

@app.get("/available_vineyards_for_purchase", response_model=List[Dict[str, Any]])
async def get_available_vineyards_for_purchase():
    return game_instance.get_available_vineyards_for_purchase()

@app.post("/buy_vineyard", response_model=Vineyard)
async def buy_vineyard(request: BuyVineyardRequest):
    print(f"[main] Received buy_vineyard request: {request.model_dump()}")
    new_vineyard = game_instance.buy_vineyard(request.vineyard_data, request.vineyard_name)
    print(f"[main] new_vineyard from game_logic: {new_vineyard}")
    if new_vineyard is None:
        print(f"[main] Raising HTTPException: Not enough money or invalid vineyard data.")
        raise HTTPException(status_code=400, detail="Not enough money or invalid vineyard data.")
    return new_vineyard

@app.post("/tend_vineyard")
async def tend_vineyard(request: TendVineyardRequest):
    success = game_instance.tend_vineyard(request.vineyard_name)
    if not success:
        raise HTTPException(status_code=400, detail="Not enough money or vineyard not found.")
    return {"message": f"Successfully tended {request.vineyard_name}."}

@app.post("/harvest_grapes", response_model=Grape)
async def harvest_grapes(request: HarvestGrapesRequest):
    harvested_grapes = game_instance.harvest_grapes(request.vineyard_name)
    if not harvested_grapes:
        raise HTTPException(status_code=400, detail="Vineyard not found or grapes not ready for harvest.")
    return harvested_grapes

@app.get("/available_vessel_types_for_purchase", response_model=List[Dict[str, Any]])
async def get_available_vessel_types_for_purchase():
    return game_instance.get_available_vessel_types_for_purchase()

@app.post("/buy_vessel", response_model=Winery)
async def buy_vessel(request: BuyVesselRequest):
    new_vessel = game_instance.buy_vessel(request.vessel_type_name)
    if not new_vessel:
        raise HTTPException(status_code=400, detail="Not enough money or invalid vessel type.")
    return game_instance.player.winery

@app.post("/process_grapes", response_model=Must)
async def process_grapes(request: ProcessGrapesRequest):
    processed_must = game_instance.process_grapes(request.grape_index, request.sort_choice, request.destem_crush_method)
    if not processed_must:
        raise HTTPException(status_code=400, detail="Invalid grape index or processing failed.")
    return processed_must

@app.post("/start_fermentation", response_model=WineInProduction)
async def start_fermentation(request: StartFermentationRequest):
    wine_in_prod = game_instance.start_fermentation(request.must_index, request.vessel_index)
    if not wine_in_prod:
        raise HTTPException(status_code=400, detail="Invalid must or vessel index, or vessel not available.")
    return wine_in_prod

@app.post("/perform_maceration_action")
async def perform_maceration_action(request: PerformMacerationActionRequest):
    success = game_instance.perform_maceration_action(request.wine_prod_index, request.action_type)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid wine in production index or action not applicable.")
    return {"message": f"Maceration action '{request.action_type}' performed."}

@app.post("/start_aging", response_model=WineInProduction)
async def start_aging(request: StartAgingRequest):
    wine_in_prod = game_instance.start_aging(request.wine_prod_index, request.vessel_index, request.aging_duration)
    if not wine_in_prod:
        raise HTTPException(status_code=400, detail="Invalid wine in production or vessel index, or vessel not available.")
    return wine_in_prod

@app.post("/bottle_wine", response_model=Wine)
async def bottle_wine(request: BottleWineRequest):
    bottled_wine = game_instance.bottle_wine(request.wine_prod_index, request.wine_name)
    if not bottled_wine:
        raise HTTPException(status_code=400, detail="Invalid wine in production index or wine not ready for bottling.")
    return bottled_wine
