# Contributing to Terroir & Time

First off, thank you for considering contributing! This project is a labor of love, and every contribution helps.

## Project Structure

The project is a monorepo containing two main packages:

-   `game-backend-new/`: The FastAPI backend application.
-   `game-frontend-new/`: The Next.js frontend application.

### Backend Structure

The backend follows a standard service-based architecture:

-   `main.py`: This is the main entry point for the FastAPI application. It defines the API endpoints (routes). The endpoints should be kept "thin," meaning they are only responsible for handling the HTTP request and response cycle.
-   `services.py`: This file contains the core business logic of the application. The `GameService` class holds all the methods that manipulate the game state. All business logic should go here.
-   `game_models.py`: This file defines the Pydantic models for API request/response validation and the SQLAlchemy ORM models for database interaction.
-   `database.py`: This file handles the database connection and session management.
-   `tests/`: This directory contains all the backend tests.

### Frontend Structure

The frontend is a Next.js application using the App Router.

-   `src/app/page.tsx`: This is the main entry point for the game's UI. It is responsible for state management and fetching data from the backend.
-   `src/app/components/`: This directory contains all the reusable React components that make up the UI. Each component should have a single responsibility.
-   `src/app/layout.tsx`: This is the main layout for the application, where global providers (like Chakra UI) are set up.

## Getting Started

Please refer to the `README.md` for instructions on how to set up and run the project.

## Development Workflow

1.  **Create a new branch:** `git checkout -b feature/your-new-feature`
2.  **Make your changes.**
3.  **Run tests:**
    -   For the backend, run `pytest` from within the `game-backend-new` directory.
    -   For the frontend, run `npm test` from within the `game-frontend-new` directory.
4.  **Submit a pull request.**

Thank you for your contributions!
