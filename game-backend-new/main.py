import os
from fastapi import FastAPI, HTTPException, Depends, Request, status, APIRouter
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from game_models import (
    Player, Vineyard, Winery, Grape, Must, WineInProduction, Wine, GameState, WineryVessel,
    BuyVineyardRequest, TendVineyardRequest, HarvestGrapesRequest, BuyVesselRequest,
    ProcessGrapesRequest, StartFermentationRequest, PerformMacerationActionRequest,
    StartAgingRequest, BottleWineRequest,
    DBPlayer, DBVineyard, DBWinery, DBGrape, DBMust, DBWineInProduction, DBWine, DBWineryVessel, DBGameState
)
from database import SessionLocal, engine, Base
from typing import List, Dict, Any, Optional
import logging

# For JWT authentication
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta

import game_models

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_database(db: Session):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or already exist.")

    game_state = db.query(DBGameState).first()
    if not game_state:
        logger.info("Initializing new game state.")
        player = DBPlayer(name="Winemaker", money=100000, reputation=50)
        db.add(player)
        db.flush()

        initial_vessels = [
            DBWineryVessel(type="Stainless Steel Tank", capacity=5000, in_use=False),
            DBWineryVessel(type="Open Top Fermenter", capacity=1000, in_use=False),
            DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
            DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
            DBWineryVessel(type="Neutral Oak Barrel (225L)", capacity=225, in_use=False),
        ]
        winery = DBWinery(name="Main Winery", player_id=player.id, vessels=initial_vessels)
        db.add(winery)
        db.flush()
        player.winery = winery

        starting_vineyard = DBVineyard(name="Home Block", varietal="Pinot Noir", region="Willamette Valley", size_acres=5, player_id=player.id)
        db.add(starting_vineyard)

        months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        game_state = DBGameState(player_id=player.id, current_year=2025, current_month_index=0, months=months_list)
        db.add(game_state)
        db.commit()
        logger.info("Game state initialized successfully.")
    else:
        logger.info("Game state already exists. Loading existing game.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    initialize_database(db)
    yield

app = FastAPI(lifespan=lifespan)
api_router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Custom exception handler for HTTPExceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException caught: {exc.detail} (Status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

# --- JWT Authentication ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key") # Use environment variable for secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(DBPlayer).filter(DBPlayer.name == username).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

@api_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, you would verify the username and password against your database
    # For this example, we'll use a hardcoded user
    if form_data.username == "Winemaker" and form_data.password == "password":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@api_router.get("/gamestate", response_model=GameState)
async def get_game_state(db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    game_instance = Game(db)
    logger.info(f"Game state requested for user {current_user.name}.")
    return game_instance.get_game_state()

@api_router.post("/advance_month", response_model=GameState)
async def advance_month(db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} advancing month.")
    game_instance = Game(db)
    game_instance.advance_month()
    logger.info("Month advanced.")
    return game_instance.get_game_state()

@api_router.get("/player", response_model=Player)
async def get_player(db: Session = Depends(get_db)):
    game_instance = Game(db)
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    logger.info("Player info requested.")
    return Player.model_validate(db_player)

@api_router.get("/vineyards", response_model=List[Vineyard])
async def get_vineyards(db: Session = Depends(get_db)):
    game_instance = Game(db)
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    logger.info("Vineyards requested.")
    return [Vineyard.model_validate(v) for v in db_player.vineyards]

@api_router.get("/winery", response_model=Winery)
async def get_winery(db: Session = Depends(get_db)):
    game_instance = Game(db)
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    db_winery = db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()
    logger.info("Winery info requested.")
    return Winery.model_validate(db_winery)

@api_router.get("/grapes_inventory", response_model=List[Grape])
async def get_grapes_inventory(db: Session = Depends(get_db)):
    game_instance = Game(db)
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    logger.info("Grapes inventory requested.")
    return [Grape.model_validate(g) for g in db_player.grapes_inventory]

@api_router.get("/bottled_wines", response_model=List[Wine])
async def get_bottled_wines(db: Session = Depends(get_db)):
    game_instance = Game(db)
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    logger.info("Bottled wines requested.")
    return [Wine.model_validate(w) for w in db_player.bottled_wines]

@api_router.get("/available_vineyards_for_purchase", response_model=List[Dict[str, Any]])
async def get_available_vineyards_for_purchase(db: Session = Depends(get_db)):
    game_instance = Game(db)
    logger.info("Available vineyards for purchase requested.")
    return game_instance.get_available_vineyards_for_purchase()

@api_router.post("/buy_vineyard", response_model=Vineyard)
async def buy_vineyard(request: BuyVineyardRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to buy vineyard: {request.vineyard_name}.")
    game_instance = Game(db)
    new_vineyard = game_instance.buy_vineyard(request.vineyard_data, request.vineyard_name)
    if new_vineyard is None:
        logger.warning(f"Failed to buy vineyard: Not enough money or invalid vineyard data for {request.vineyard_name}.")
        raise HTTPException(status_code=400, detail="Not enough money or invalid vineyard data.")
    logger.info(f"Vineyard {new_vineyard.name} purchased by {current_user.name}.")
    return new_vineyard

@api_router.post("/tend_vineyard")
async def tend_vineyard(request: TendVineyardRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to tend vineyard: {request.vineyard_name}.")
    game_instance = Game(db)
    success = game_instance.tend_vineyard(request.vineyard_name)
    if not success:
        logger.warning(f"Failed to tend vineyard: Not enough money or vineyard not found for {request.vineyard_name}.")
        raise HTTPException(status_code=400, detail="Not enough money or vineyard not found.")
    logger.info(f"Successfully tended {request.vineyard_name} by {current_user.name}.")
    return {"message": f"Successfully tended {request.vineyard_name}."}

@api_router.post("/harvest_grapes", response_model=Grape)
async def harvest_grapes(request: HarvestGrapesRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to harvest grapes from: {request.vineyard_name}.")
    game_instance = Game(db)
    harvested_grapes = game_instance.harvest_grapes(request.vineyard_name)
    if not harvested_grapes:
        logger.warning(f"Failed to harvest grapes: Vineyard not found or grapes not ready for harvest for {request.vineyard_name}.")
        raise HTTPException(status_code=400, detail="Vineyard not found or grapes not ready for harvest.")
    logger.info(f"Grapes harvested from {request.vineyard_name} by {current_user.name}.")
    return harvested_grapes

@api_router.get("/available_vessel_types_for_purchase", response_model=List[Dict[str, Any]])
async def get_available_vessel_types_for_purchase(db: Session = Depends(get_db)):
    game_instance = Game(db)
    logger.info("Available vessel types for purchase requested.")
    return game_instance.get_available_vessel_types_for_purchase()

@api_router.post("/buy_vessel", response_model=Winery)
async def buy_vessel(request: BuyVesselRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to buy vessel: {request.vessel_type_name}.")
    game_instance = Game(db)
    new_vessel = game_instance.buy_vessel(request.vessel_type_name)
    if not new_vessel:
        logger.warning(f"Failed to buy vessel: Not enough money or invalid vessel type for {request.vessel_type_name}.")
        raise HTTPException(status_code=400, detail="Not enough money or invalid vessel type.")
    
    db_game_state = db.query(DBGameState).first()
    db_player = db.query(DBPlayer).filter(DBPlayer.id == db_game_state.player_id).first()
    db_winery = db.query(DBWinery).filter(DBWinery.player_id == db_player.id).first()
    logger.info(f"Vessel {new_vessel.type} purchased by {current_user.name}.")
    return Winery.model_validate(db_winery)

@api_router.post("/process_grapes", response_model=Must)
async def process_grapes(request: ProcessGrapesRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to process grapes (index {request.grape_index}).")
    game_instance = Game(db)
    processed_must = game_instance.process_grapes(request.grape_index, request.sort_choice, request.destem_crush_method)
    if not processed_must:
        logger.warning(f"Failed to process grapes: Invalid grape index or processing failed for index {request.grape_index}.")
        raise HTTPException(status_code=400, detail="Invalid grape index or processing failed.")
    logger.info(f"Grapes processed into must: {processed_must.varietal} by {current_user.name}.")
    return processed_must

@api_router.post("/start_fermentation", response_model=WineInProduction)
async def start_fermentation(request: StartFermentationRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to start fermentation for must index {request.must_index}.")
    game_instance = Game(db)
    wine_in_prod = game_instance.start_fermentation(request.must_index, request.vessel_index)
    if not wine_in_prod:
        logger.warning(f"Failed to start fermentation: Invalid must or vessel index, or vessel not available for must index {request.must_index}, vessel index {request.vessel_index}.")
        raise HTTPException(status_code=400, detail="Invalid must or vessel index, or vessel not available.")
    logger.info(f"Fermentation started for {wine_in_prod.varietal} by {current_user.name}.")
    return wine_in_prod

@api_router.post("/perform_maceration_action")
async def perform_maceration_action(request: PerformMacerationActionRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to perform maceration action '{request.action_type}' for wine in production index {request.wine_prod_index}.")
    game_instance = Game(db)
    success = game_instance.perform_maceration_action(request.wine_prod_index, request.action_type)
    if not success:
        logger.warning(f"Failed to perform maceration action: Invalid wine in production index or action not applicable for index {request.wine_prod_index}, action {request.action_type}.")
        raise HTTPException(status_code=400, detail="Invalid wine in production index or action not applicable.")
    logger.info(f"Maceration action '{request.action_type}' performed for wine in production index {request.wine_prod_index} by {current_user.name}.")
    return {"message": f"Maceration action '{request.action_type}' performed."}

@api_router.post("/start_aging", response_model=WineInProduction)
async def start_aging(request: StartAgingRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to start aging for wine in production index {request.wine_prod_index}.")
    game_instance = Game(db)
    wine_in_prod = game_instance.start_aging(request.wine_prod_index, request.vessel_index, request.aging_duration)
    if not wine_in_prod:
        logger.warning(f"Failed to start aging: Invalid wine in production or vessel index, or vessel not available for index {request.wine_prod_index}, vessel index {request.vessel_index}.")
        raise HTTPException(status_code=400, detail="Invalid wine in production or vessel index, or vessel not available.")
    logger.info(f"Aging started for {wine_in_prod.varietal} by {current_user.name}.")
    return wine_in_prod

@api_router.post("/bottle_wine", response_model=Wine)
async def bottle_wine(request: BottleWineRequest, db: Session = Depends(get_db), current_user: DBPlayer = Depends(get_current_user)):
    logger.info(f"User {current_user.name} attempting to bottle wine '{request.wine_name}' from index {request.wine_prod_index}.")
    game_instance = Game(db)
    bottled_wine = game_instance.bottle_wine(request.wine_prod_index, request.wine_name)
    if not bottled_wine:
        logger.warning(f"Failed to bottle wine: Invalid wine in production index or wine not ready for bottling for index {request.wine_prod_index}.")
        raise HTTPException(status_code=400, detail="Invalid wine in production index or wine not ready for bottling.")
    logger.info(f"Wine '{bottled_wine.name}' bottled by {current_user.name}.")
    return bottled_wine

app.include_router(api_router, prefix="/api")
app.mount("/", StaticFiles(directory="static", html=True), name="static")
