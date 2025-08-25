import logging
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from game_logic import Game, REGIONS, GRAPE_CHARACTERISTICS, VESSEL_TYPES
from game_models import DBGameState, DBPlayer, DBWinery, GameState, Player

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_database(db: Session):
    """Initializes the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
    logging.info("Database initialized.")

def start_new_game(db: Session):
    """Starts a new game by creating the initial game state."""
    logging.info("No existing game found. Starting a new game.")

    # Create a new player and winery
    new_player = DBPlayer(name="Winemaker", money=100000, reputation=50)
    db.add(new_player)
    db.commit()
    db.refresh(new_player)

    new_winery = DBWinery(player_id=new_player.id, name="My First Winery")
    db.add(new_winery)
    db.commit()
    db.refresh(new_winery)

    new_player.winery = new_winery
    db.commit()
    db.refresh(new_player)

    # Create the initial game state
    initial_game_state = DBGameState(
        player_id=new_player.id,
        current_year=2024,
        current_month_index=0,  # Starting in January
        months=["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]
    )
    db.add(initial_game_state)
    db.commit()
    logging.info("New game started successfully.")

def display_game_state(game_state: GameState):
    """Prints the current game state to the console."""
    player = game_state.player
    current_month = game_state.months[game_state.current_month_index]

    print("\n" + "="*50)
    print(f"== {player.name}'s Winemaking Saga ==")
    print(f"== {current_month}, {game_state.current_year} ==")
    print("="*50)
    print(f"Money: ${player.money:,.2f} | Reputation: {player.reputation}")
    print("\n--- Vineyards ---")
    if not player.vineyards:
        print("You own no vineyards.")
    else:
        for v in player.vineyards:
            status = "Ready to Harvest" if v.grapes_ready else "Growing"
            print(f"- {v.name} ({v.varietal}, {v.size_acres} acres) - Health: {v.health}% - Status: {status}")

    print(f"\n--- Winery: {player.winery.name} ---")
    if player.winery:
        print(f"Vessels: {len(player.winery.vessels)}")
        print(f"Must in production: {len(player.winery.must_in_production)}")
        print(f"Wines fermenting: {len(player.winery.wines_fermenting)}")
        print(f"Wines aging: {len(player.winery.wines_aging)}")

    print("\n--- Grapes Inventory ---")
    if not player.grapes_inventory:
        print("You have no harvested grapes.")
    else:
        for i, g in enumerate(player.grapes_inventory):
            print(f"{i+1}. {g.quantity_kg}kg of {g.varietal} ({g.vintage}) - Quality: {g.quality}")

    print("\n--- Bottled Wines ---")
    if not player.bottled_wines:
        print("You have no bottled wines.")
    else:
        for w in player.bottled_wines:
            print(f"- {w.name} ({w.varietal} {w.vintage}) - {w.bottles} bottles - Quality: {w.quality}")

    print("\n" + "="*50 + "\n")

def handle_buy_vineyard(game: Game):
    """Handles the logic for buying a new vineyard."""
    available = game.get_available_vineyards_for_purchase()
    print("\n--- Vineyards for Sale ---")
    for i, v in enumerate(available):
        print(f"{i+1}. {v['varietal']} vineyard in {v['region']} for ${v['cost']:,}")

    try:
        choice = int(input("Choose a vineyard to buy (or 0 to go back): "))
        if choice == 0 or choice > len(available):
            return

        selected_vineyard = available[choice-1]
        name = input(f"Enter a name for your new {selected_vineyard['varietal']} vineyard: ")

        result = game.buy_vineyard(selected_vineyard, name)
        if result:
            print(f"Congratulations! You have purchased '{name}'.")
        else:
            print("Could not purchase the vineyard. Not enough money?")
    except ValueError:
        print("Invalid input.")

def handle_tend_vineyard(game: Game, player: Player):
    """Handles the logic for tending to a vineyard."""
    if not player.vineyards:
        print("You have no vineyards to tend.")
        return

    print("\n--- Tend to a Vineyard ---")
    for i, v in enumerate(player.vineyards):
        print(f"{i+1}. {v.name} (Health: {v.health}%)")

    try:
        choice = int(input("Choose a vineyard to tend (or 0 to go back): "))
        if choice == 0 or choice > len(player.vineyards):
            return

        vineyard_name = player.vineyards[choice-1].name
        if game.tend_vineyard(vineyard_name):
            print(f"You have tended to {vineyard_name}.")
        else:
            print(f"Could not tend to {vineyard_name}. Not enough money?")
    except ValueError:
        print("Invalid input.")

def handle_harvest_grapes(game: Game, player: Player):
    """Handles the logic for harvesting grapes."""
    ready_for_harvest = [v for v in player.vineyards if v.grapes_ready]
    if not ready_for_harvest:
        print("You have no vineyards ready for harvest.")
        return

    print("\n--- Harvest Grapes ---")
    for i, v in enumerate(ready_for_harvest):
        print(f"{i+1}. {v.name} ({v.varietal})")

    try:
        choice = int(input("Choose a vineyard to harvest (or 0 to go back): "))
        if choice == 0 or choice > len(ready_for_harvest):
            return

        vineyard_name = ready_for_harvest[choice-1].name
        result = game.harvest_grapes(vineyard_name)
        if result:
            print(f"Successfully harvested {result.quantity_kg}kg of {result.varietal} grapes.")
        else:
            print("Failed to harvest grapes.")
    except ValueError:
        print("Invalid input.")

def handle_winery_management(game: Game, player: Player):
    # This is a placeholder for a more complex winery management menu
    print("\nWinery Management is not fully implemented yet.")
    print("1. Buy a new vessel")
    # Add more options here later
    choice = input("> ")
    if choice == '1':
        handle_buy_vessel(game)

def handle_buy_vessel(game: Game):
    """Handles logic for buying a new vessel."""
    available = game.get_available_vessel_types_for_purchase()
    print("\n--- Vessels for Sale ---")
    for i, v in enumerate(available):
        print(f"{i+1}. {v['name']} ({v['capacity']}L) - ${v['cost']:,}")

    try:
        choice = int(input("Choose a vessel to buy (or 0 to go back): "))
        if choice == 0 or choice > len(available):
            return

        vessel_name = available[choice-1]['name']
        result = game.buy_vessel(vessel_name)
        if result:
            print(f"Successfully purchased a {vessel_name}.")
        else:
            print("Could not purchase the vessel. Not enough money?")
    except ValueError:
        print("Invalid input.")

def main():
    """The main game loop."""
    db = SessionLocal()
    init_database(db)

    # Check if a game state exists, if not, start a new game
    if db.query(DBGameState).first() is None:
        start_new_game(db)

    game = Game(db)

    while True:
        current_state = game.get_game_state()
        display_game_state(current_state)

        print("What would you like to do?")
        print("1. Advance to next month")
        print("2. Buy a new vineyard")
        print("3. Tend to a vineyard")
        print("4. Harvest grapes")
        print("5. Manage winery")
        print("6. Exit game")

        choice = input("> ")

        if choice == '1':
            game.advance_month()
        elif choice == '2':
            handle_buy_vineyard(game)
        elif choice == '3':
            handle_tend_vineyard(game, current_state.player)
        elif choice == '4':
            handle_harvest_grapes(game, current_state.player)
        elif choice == '5':
            handle_winery_management(game, current_state.player)
        elif choice == '6':
            print("Thank you for playing Terroir & Time!")
            break
        else:
            print("Invalid choice, please try again.")

    db.close()

if __name__ == "__main__":
    main()
