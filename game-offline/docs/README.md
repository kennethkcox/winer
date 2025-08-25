# Terroir & Time: Offline Edition

Welcome to the Offline Edition of "Terroir & Time," a simulation game where you embark on the journey of a natural winemaker. This version of the game runs entirely on your local machine, with no internet connection required.

## Getting Started

To play the game, you'll need Python and a few libraries.

### Prerequisites

*   Python 3.9+

### Setup

1.  **Navigate to the offline game directory:**
    ```bash
    cd game-offline
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    The game requires `sqlalchemy` and `pydantic`. You can install them using pip:
    ```bash
    pip install sqlalchemy pydantic
    ```

### Running the Game

Once the setup is complete, you can start the game by running the `main_cli.py` script:

```bash
python main_cli.py
```

The game will start, and you will be presented with the main menu.

## How to Play

The game is played through a command-line interface. On each turn, you will see the current game state, followed by a list of actions you can take.

The core gameplay loop involves:

*   **Advancing Time:** Choose "Advance to next month" to move the game forward. This will trigger monthly updates, such as vine growth and wine aging.
*   **Managing Resources:** Keep an eye on your money and reputation.
*   **Vineyard Management:**
    *   **Buy Vineyards:** Purchase new vineyards from different regions.
    *   **Tend Vineyards:** Improve the health of your vineyards by tending to them.
*   **Harvesting:** Harvest grapes when they are ripe (usually in September/October).
*   **Winery Management:**
    *   **Buy Vessels:** Purchase vessels like tanks and barrels to equip your winery.
    *   *(More winery features to come!)*

The game automatically saves your progress in a `game.db` file within the `game-offline` directory. The next time you run the game, your progress will be restored.
