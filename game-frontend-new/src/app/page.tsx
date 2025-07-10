"use client";

import { useState, useEffect } from "react";
import { Container, Row, Col, Card, Button, Navbar, Nav } from "react-bootstrap";

interface Vineyard {
  id?: number;
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
  id?: number;
  type: string;
  capacity: number;
  in_use: boolean;
}

interface Winery {
  id?: number;
  name: string;
  vessels: WineryVessel[];
  must_in_production: Must[];
  wines_fermenting: WineInProduction[];
  wines_aging: WineInProduction[];
}

interface Grape {
  id?: number;
  varietal: string;
  vintage: number;
  quantity_kg: number;
  quality: number;
}

interface Must {
  id?: number;
  varietal: string;
  vintage: number;
  quantity_kg: number;
  quality: number;
  processing_method: string;
  destem_crush_method: string;
  fermented: boolean;
}

interface WineInProduction {
  id?: number;
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
  id?: number;
  name: string;
  vintage: number;
  varietal: string;
  style: string;
  quality: number;
  bottles: number;
}

interface Player {
  id?: number;
  name: string;
  money: number;
  reputation: number;
  vineyards: Vineyard[];
  winery: Winery;
  grapes_inventory: Grape[];
  bottled_wines: Wine[];
}

interface GameState {
  id?: number;
  player: Player;
  current_year: number;
  current_month_index: number;
  months: string[];
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchGameState();
  }, []);

  const fetchGameState = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/`);
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
      const response = await fetch(`${BACKEND_URL}/advance_month`, {
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
    <>
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand href="#home">Terroir & Time</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="#game">Game Status</Nav.Link>
              <Nav.Link href="#vineyards">Vineyards</Nav.Link>
              <Nav.Link href="#winery">Winery</Nav.Link>
              <Nav.Link href="#inventory">Inventory</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mt-5">
        <h1 className="text-center mb-4">Terroir & Time: A Natural Winemaking Saga</h1>

        {/* Game Status Section */}
        <Row id="game" className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <Card.Title className="text-primary">Game Status</Card.Title>
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
                <Button variant="success" onClick={handleAdvanceMonth} disabled={loading}>
                  {loading ? "Advancing..." : "Advance Month"}
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Player Info Section */}
        <Row className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <Card.Title className="text-primary">Player Info</Card.Title>
                <Card.Text>
                  <strong>Name:</strong> {player.name}
                </Card.Text>
                <Card.Text>
                  <strong>Vineyards Owned:</strong> {player.vineyards.length}
                </Card.Text>
                <Card.Text>
                  <strong>Winery Vessels:</strong> {player.winery?.vessels.length || 0}
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Vineyards Section */}
        <Row id="vineyards" className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <Card.Title className="text-primary">Your Vineyards</Card.Title>
                {player.vineyards.length === 0 ? (
                  <Card.Text>You don't own any vineyards yet. Time to buy one!</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.vineyards.map((vineyard, index) => (
                      <Col key={index}>
                        <Card className="h-100">
                          <Card.Body>
                            <Card.Title>{vineyard.name} ({vineyard.varietal})</Card.Title>
                            <Card.Text>Region: {vineyard.region}</Card.Text>
                            <Card.Text>Size: {vineyard.size_acres} acres</Card.Text>
                            <Card.Text>Health: {vineyard.health}%</Card.Text>
                            <Card.Text>Grapes Ready: {vineyard.grapes_ready ? "Yes" : "No"}</Card.Text>
                            <Card.Text>Harvested This Year: {vineyard.harvested_this_year ? "Yes" : "No"}</Card.Text>
                            {/* Add actions like Tend, Harvest here */}
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Winery Section */}
        <Row id="winery" className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <Card.Title className="text-primary">Your Winery</Card.Title>
                <Card.Text>Winery Name: {player.winery?.name || "N/A"}</Card.Text>
                <h5>Vessels:</h5>
                {player.winery?.vessels.length === 0 ? (
                  <Card.Text>No vessels in your winery yet.</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.winery?.vessels.map((vessel, index) => (
                      <Col key={index}>
                        <Card className="h-100">
                          <Card.Body>
                            <Card.Title>{vessel.type}</Card.Title>
                            <Card.Text>Capacity: {vessel.capacity}L</Card.Text>
                            <Card.Text>In Use: {vessel.in_use ? "Yes" : "No"}</Card.Text>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
                {/* Add sections for Must, Fermenting, Aging wines */}
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Inventory Section */}
        <Row id="inventory" className="mb-4">
          <Col>
            <Card className="shadow-sm">
              <Card.Body>
                <Card.Title className="text-primary">Inventory</Card.Title>
                <h5>Grapes:</h5>
                {player.grapes_inventory.length === 0 ? (
                  <Card.Text>No grapes in inventory.</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.grapes_inventory.map((grape, index) => (
                      <Col key={index}>
                        <Card className="h-100">
                          <Card.Body>
                            <Card.Title>{grape.varietal} ({grape.vintage})</Card.Title>
                            <Card.Text>Quantity: {grape.quantity_kg} kg</Card.Text>
                            <Card.Text>Quality: {grape.quality}</Card.Text>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}

                <h5 className="mt-4">Bottled Wines:</h5>
                {player.bottled_wines.length === 0 ? (
                  <Card.Text>No bottled wines yet.</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.bottled_wines.map((wine, index) => (
                      <Col key={index}>
                        <Card className="h-100">
                          <Card.Body>
                            <Card.Title>{wine.name} ({wine.vintage})</Card.Title>
                            <Card.Text>Varietal: {wine.varietal}</Card.Text>
                            <Card.Text>Style: {wine.style}</Card.Text>
                            <Card.Text>Quality: {wine.quality}</Card.Text>
                            <Card.Text>Bottles: {wine.bottles}</Card.Text>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
              </Card.Body>
            </Card>
          </Col>
        </Row>

      </Container>
    </>
  );
}
