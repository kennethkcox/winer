"use client";

import { useState, useEffect } from "react";
import { Container, Row, Col, Card, Button } from "react-bootstrap";

interface Vineyard {
  name: string;
  varietal: string;
  region: string;
  size_acres: number;
  age_of_vines: number;
  soil_type: string;
  health: number;
  grapes_ready: boolean;
  harvested_this_year: boolean;
}

interface WineryVessel {
  type: string;
  capacity: number;
  in_use: boolean;
}

interface Winery {
  name: string;
  vessels: WineryVessel[];
  must_in_production: any[]; // Define Must interface later
  wines_fermenting: any[]; // Define WineInProduction interface later
  wines_aging: any[]; // Define WineInProduction interface later
}

interface Grape {
  varietal: string;
  vintage: number;
  quantity_kg: number;
  quality: number;
}

interface Must {
  varietal: string;
  vintage: number;
  quantity_kg: number;
  quality: number;
  processing_method: string;
  destem_crush_method: string;
  fermented: boolean;
}

interface WineInProduction {
  varietal: string;
  vintage: number;
  quantity_liters: number;
  quality: number;
  vessel_type: string;
  vessel_index: number;
  stage: string;
  fermentation_progress: number;
  aging_progress: number;
  aging_duration: number;
  maceration_actions_taken: number;
}

interface Wine {
  name: string;
  vintage: number;
  varietal: string;
  style: string;
  quality: number;
  bottles: number;
}

interface Player {
  name: string;
  money: number;
  reputation: number;
  vineyards: Vineyard[];
  winery: Winery;
  grapes_inventory: Grape[];
  bottled_wines: Wine[];
}

interface GameState {
  player: Player;
  current_year: number;
  current_month_index: number;
  months: string[];
}

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGameState();
  }, []);

  const fetchGameState = async () => {
    try {
      const response = await fetch("http://localhost:8000/");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: GameState = await response.json();
      setGameState(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceMonth = async () => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/advance_month", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data: GameState = await response.json();
      setGameState(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p>Loading game...</p>;
  if (error) return <p>Error: {error}</p>;
  if (!gameState) return <p>No game state available.</p>;

  const { player, current_year, current_month_index, months } = gameState;

  return (
    <Container className="mt-5">
      <h1 className="text-center mb-4">Terroir & Time: A Natural Winemaking Saga</h1>

      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Game Status</Card.Title>
              <Card.Text>
                <strong>Date:</strong> {months[current_month_index]}, {current_year}
              </Card.Text>
              <Card.Text>
                <strong>Money:</strong> ${player.money.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </Card.Text>
              <Card.Text>
                <strong>Reputation:</strong> {player.reputation}/100
              </Card.Text>
              <Card.Text>
                <strong>Grapes:</strong> {(player.grapes_inventory || []).reduce((sum, g) => sum + g.quantity_kg, 0)} kg
              </Card.Text>
              <Card.Text>
                <strong>Bottled Wine:</strong> {(player.bottled_wines || []).reduce((sum, w) => sum + w.bottles, 0)} bottles
              </Card.Text>
              <Button variant="primary" onClick={handleAdvanceMonth} disabled={loading}>
                {loading ? "Advancing..." : "Advance Month"}
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Player Info</Card.Title>
              <Card.Text>
                <strong>Name:</strong> {player.name}
              </Card.Text>
              <Card.Text>
                <strong>Vineyards:</strong> {player.vineyards.length}
              </Card.Text>
              <Card.Text>
                <strong>Winery Vessels:</strong> {player.winery?.vessels.length || 0}
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}