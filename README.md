# Terroir & Time: A Natural Winemaking Saga

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Welcome to "Terroir & Time," a simulation game where you embark on the journey of a natural winemaker. From purchasing your first vineyard to bottling your unique creations, every decision you make will shape your wine and your legacy.

This project is a full-stack application featuring a Python-based backend and a modern web-based frontend.

## Deploy to Heroku

You can deploy this application to Heroku with a single click using the "Deploy to Heroku" button above. This will automatically configure the application and deploy it to a new Heroku app.

**Note:** You will need to replace the placeholder `repository` and `logo` URLs in the `app.json` file with your own GitHub repository URL and a link to your logo.

## Project Structure

The repository is organized into two main components:

*   `game-backend-new/`: A backend server built with Python and the FastAPI framework. It handles all game logic, state management, and data persistence.
*   `game-frontend-new/`: A responsive user interface built with Next.js (a React framework) and TypeScript. It communicates with the backend to provide an interactive gaming experience.

## Getting Started

To run the full application, you will need to set up and run both the backend and frontend services.

### Prerequisites

*   Python 3.9+
*   Node.js 20+
*   Docker (optional, for containerized deployment)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd game-backend-new
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend API will now be available at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd game-frontend-new
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

3.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The frontend application will now be available at `http://localhost:3000`.

## How to Play

Once both the frontend and backend are running, open your web browser and navigate to `http://localhost:3000`. The game will load, and you can begin your winemaking journey.

The core gameplay loop involves:

*   **Advancing Time:** Click the "Advance Month" button to move the game forward.
*   **Managing Resources:** Keep an eye on your money and reputation.
*   **Vineyard Management:** Purchase and tend to your vineyards.
*   **Harvesting:** Harvest grapes when they are ready.
*   **Winemaking:** Process grapes, ferment must, and age wine.
*   **Bottling:** Bottle your finished wine and build your inventory.

## API Endpoints

The backend provides a RESTful API to manage the game state. You can explore the interactive API documentation (Swagger UI) by navigating to `http://localhost:8000/docs` when the backend server is running.

The following are the primary endpoints:

*   `GET /`: Get the current game state.
*   `POST /advance_month`: Advance the game by one month.
*   `GET /player`: Get player information.
*   `GET /vineyards`: Get a list of the player's vineyards.
*   `GET /winery`: Get information about the player's winery.
*   `POST /buy_vineyard`: Purchase a new vineyard.
*   `POST /tend_vineyard`: Tend to a vineyard.
*   `POST /harvest_grapes`: Harvest grapes from a vineyard.
*   `POST /buy_vessel`: Purchase a new vessel for the winery.
*   `POST /process_grapes`: Process harvested grapes into must.
*   `POST /start_fermentation`: Start the fermentation process.
*   `POST /start_aging`: Start the aging process for a wine.
*   `POST /bottle_wine`: Bottle a finished wine.

## Technologies Used

*   **Backend:**
    *   Python
    *   FastAPI
    *   Uvicorn
    *   Pydantic
*   **Frontend:**
    *   Next.js
    *   React
    *   TypeScript
    *   Bootstrap

## Docker Deployment

For a more streamlined deployment, you can use Docker to run both the frontend and backend in containers. Dockerfiles are provided in both the `game-backend-new` and `game-frontend-new` directories. You can use a `docker-compose.yml` file to orchestrate the services.