"use client";

import { useState, useEffect } from "react";
import { Container, Row, Col, Card, Button, Navbar, Nav, Form, Alert, Modal } from "react-bootstrap";

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

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "";

export default function Home() {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [token, setToken] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);

  const [showBuyVineyardModal, setShowBuyVineyardModal] = useState(false);
  const [selectedVineyardToBuy, setSelectedVineyardToBuy] = useState<any>(null);
  const [newVineyardName, setNewVineyardName] = useState<string>("");
  const [buyVineyardError, setBuyVineyardError] = useState<string | null>(null);

  const [showBuyVesselModal, setShowBuyVesselModal] = useState(false);
  const [selectedVesselToBuy, setSelectedVesselToBuy] = useState<any>(null);
  const [buyVesselError, setBuyVesselError] = useState<string | null>(null);

  const [showProcessGrapesModal, setShowProcessGrapesModal] = useState(false);
  const [selectedGrapeToProcess, setSelectedGrapeToProcess] = useState<Grape | null>(null);
  const [processGrapesError, setProcessGrapesError] = useState<string | null>(null);
  const [sortChoice, setSortChoice] = useState<string>("no");
  const [destemCrushMethod, setDestemCrushMethod] = useState<string>("Destemmed/Crushed");

  const [showStartFermentationModal, setShowStartFermentationModal] = useState(false);
  const [selectedMustToFerment, setSelectedMustToFerment] = useState<Must | null>(null);
  const [selectedVesselForFermentation, setSelectedVesselForFermentation] = useState<number | null>(null);
  const [startFermentationError, setStartFermentationError] = useState<string | null>(null);

  const [showBottleWineModal, setShowBottleWineModal] = useState(false);
  const [selectedWineToBottle, setSelectedWineToBottle] = useState<WineInProduction | null>(null);
  const [newWineName, setNewWineName] = useState<string>("");
  const [bottleWineError, setBottleWineError] = useState<string | null>(null);

  const [regions, setRegions] = useState<any>({});
  const [vesselTypes, setVesselTypes] = useState<any>({});
  const [grapeCharacteristics, setGrapeCharacteristics] = useState<any>({});

  useEffect(() => {
    const fetchGameData = async () => {
      try {
        const [regionsRes, vesselsRes, grapesRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/game_data/regions`),
          fetch(`${BACKEND_URL}/api/game_data/vessel_types`),
          fetch(`${BACKEND_URL}/api/game_data/grape_characteristics`),
        ]);
        setRegions(await regionsRes.json());
        setVesselTypes(await vesselsRes.json());
        setGrapeCharacteristics(await grapesRes.json());
      } catch (e) {
        setError("Failed to load game data.");
      }
    };

    fetchGameData();

    const storedToken = localStorage.getItem("accessToken");
    if (storedToken) {
      setToken(storedToken);
      fetchGameState(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchGameState = async (authToken: string | null = token) => {
    setLoading(true);
    setError(null);
    try {
      const headers: HeadersInit = {};
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      const response = await fetch(`${BACKEND_URL}/api/gamestate`, {
        headers: headers,
      });
      if (!response.ok) {
        if (response.status === 401) {
          setLoginError("Unauthorized. Please log in.");
          setToken(null);
          localStorage.removeItem("accessToken");
        }
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
      const response = await fetch(`${BACKEND_URL}/api/advance_month`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        if (response.status === 401) {
          setLoginError("Unauthorized. Please log in.");
          setToken(null);
          localStorage.removeItem("accessToken");
        }
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

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError(null);
    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${BACKEND_URL}/api/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      localStorage.setItem("accessToken", data.access_token);
      setToken(data.access_token);
      await fetchGameState(data.access_token); // Fetch game state with new token
    } catch (e: any) {
      setLoginError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem("accessToken");
    setGameState(null);
    setLoginError(null);
    setUsername("");
    setPassword("");
    setLoading(false);
  };

  const handleBuyVineyard = async () => {
    if (!selectedVineyardToBuy || !newVineyardName) return;
    setBuyVineyardError(null);
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/buy_vineyard`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          vineyard_data: selectedVineyardToBuy,
          vineyard_name: newVineyardName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState(); // Refresh game state
      setShowBuyVineyardModal(false);
      setNewVineyardName("");
      setSelectedVineyardToBuy(null);
    } catch (e: any) {
      setBuyVineyardError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTendVineyard = async (vineyardName: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/tend_vineyard`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vineyard_name: vineyardName }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHarvestGrapes = async (vineyardName: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/harvest_grapes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vineyard_name: vineyardName }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBuyVessel = async () => {
    if (!selectedVesselToBuy) return;
    setBuyVesselError(null);
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/buy_vessel`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vessel_type_name: selectedVesselToBuy.name }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState(); // Refresh game state
      setShowBuyVesselModal(false);
      setSelectedVesselToBuy(null);
    } catch (e: any) {
      setBuyVesselError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProcessGrapes = async () => {
    if (!selectedGrapeToProcess) return;
    setProcessGrapesError(null);
    setLoading(true);
    try {
      const grapeIndex = gameState?.player.grapes_inventory.findIndex(g => g.id === selectedGrapeToProcess.id) ?? -1;
      if (grapeIndex === -1) {
        throw new Error("Selected grape not found in inventory.");
      }

      const response = await fetch(`${BACKEND_URL}/api/process_grapes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          grape_index: grapeIndex,
          sort_choice: sortChoice,
          destem_crush_method: destemCrushMethod,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
      setShowProcessGrapesModal(false);
    } catch (e: any) {
      setProcessGrapesError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartFermentation = async () => {
    if (selectedMustToFerment === null || selectedVesselForFermentation === null) return;
    setStartFermentationError(null);
    setLoading(true);
    try {
      const mustIndex = gameState?.player.winery.must_in_production.findIndex(m => m.id === selectedMustToFerment.id) ?? -1;
      if (mustIndex === -1) {
        throw new Error("Selected must not found in inventory.");
      }

      const response = await fetch(`${BACKEND_URL}/api/start_fermentation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          must_index: mustIndex,
          vessel_index: selectedVesselForFermentation,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
      setShowStartFermentationModal(false);
    } catch (e: any) {
      setStartFermentationError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePerformMaceration = async (wineProdIndex: number) => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/perform_maceration_action`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          wine_prod_index: wineProdIndex,
          action_type: "Punch Down",
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBottleWine = async () => {
    if (!selectedWineToBottle || !newWineName) return;
    setBottleWineError(null);
    setLoading(true);
    try {
      const wineProdIndex = gameState?.player.winery.wines_aging.findIndex(w => w.id === selectedWineToBottle.id) ?? -1;
      if (wineProdIndex === -1) {
        throw new Error("Selected wine not found in aging inventory.");
      }

      const response = await fetch(`${BACKEND_URL}/api/bottle_wine`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          wine_prod_index: wineProdIndex,
          wine_name: newWineName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
      setShowBottleWineModal(false);
      setNewWineName("");
    } catch (e: any) {
      setBottleWineError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !gameState) return <p>Loading game...</p>;
  if (error) return <p>Error: {error}</p>;

  if (!token || !gameState) {
    return (
      <Container className="mt-5">
        <h1 className="text-center mb-4">Terroir & Time: A Natural Winemaking Saga</h1>
        <Row className="justify-content-md-center">
          <Col md={6}>
            <Card className="shadow-sm bg-dark text-white">
              <Card.Body>
                <Card.Title className="text-primary text-center">Login</Card.Title>
                {loginError && <Alert variant="danger">{loginError}</Alert>}
                <Form onSubmit={handleLogin}>
                  <Form.Group className="mb-3" controlId="formBasicEmail">
                    <Form.Label>Username</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Enter username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      required
                      className="bg-secondary text-white border-secondary"
                    />
                  </Form.Group>

                  <Form.Group className="mb-3" controlId="formBasicPassword">
                    <Form.Label>Password</Form.Label>
                    <Form.Control
                      type="password"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="bg-secondary text-white border-secondary"
                    />
                  </Form.Group>
                  <Button variant="primary" type="submit" disabled={loading} className="w-100">
                    {loading ? "Logging in..." : "Login"}
                  </Button>
                </Form>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

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
            <Nav>
              <Button variant="outline-light" onClick={handleLogout}>Logout</Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mt-5 text-white">
        <h1 className="text-center mb-4 text-primary">Terroir & Time: A Natural Winemaking Saga</h1>

        {/* Game Status Section */}
        <Row id="game" className="mb-4">
          <Col>
            <Card className="shadow-sm bg-dark text-white">
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
            <Card className="shadow-sm bg-dark text-white">
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
            <Card className="shadow-sm bg-dark text-white">
              <Card.Body>
                <Card.Title className="text-primary">Your Vineyards</Card.Title>
                {player.vineyards.length === 0 ? (
                  <Card.Text>You don&apos;t own any vineyards yet. Time to buy one!</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.vineyards.map((vineyard, index) => (
                      <Col key={index}>
                        <Card className="h-100 bg-secondary text-white">
                          <Card.Body>
                            <Card.Title>{vineyard.name} ({vineyard.varietal})</Card.Title>
                            <Card.Text>Region: {vineyard.region}</Card.Text>
                            <Card.Text>Size: {vineyard.size_acres} acres</Card.Text>
                            <Card.Text>Health: {vineyard.health}%</Card.Text>
                            <Card.Text>Grapes Ready: {vineyard.grapes_ready ? "Yes" : "No"}</Card.Text>
                            <Card.Text>Harvested This Year: {vineyard.harvested_this_year ? "Yes" : "No"}</Card.Text>
                            <Button
                              variant="info"
                              className="me-2"
                              onClick={() => handleTendVineyard(vineyard.name)}
                              disabled={loading}
                            >
                              Tend
                            </Button>
                            <Button
                              variant="warning"
                              onClick={() => handleHarvestGrapes(vineyard.name)}
                              disabled={loading || !vineyard.grapes_ready || vineyard.harvested_this_year}
                            >
                              Harvest
                            </Button>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
                <Button variant="primary" className="mt-3" onClick={() => setShowBuyVineyardModal(true)}>
                  Buy New Vineyard
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Winery Section */}
        <Row id="winery" className="mb-4">
          <Col>
            <Card className="shadow-sm bg-dark text-white">
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
                        <Card className="h-100 bg-secondary text-white">
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
                <Button variant="primary" className="mt-3" onClick={() => setShowBuyVesselModal(true)}>
                  Buy New Vessel
                </Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Inventory Section */}
        <Row id="inventory" className="mb-4">
          <Col>
            <Card className="shadow-sm bg-dark text-white">
              <Card.Body>
                <Card.Title className="text-primary">Inventory</Card.Title>
                <h5>Grapes:</h5>
                {player.grapes_inventory.length === 0 ? (
                  <Card.Text>No grapes in inventory.</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.grapes_inventory.map((grape, index) => (
                      <Col key={index}>
                        <Card className="h-100 bg-secondary text-white">
                          <Card.Body>
                            <Card.Title>{grape.varietal} ({grape.vintage})</Card.Title>
                            <Card.Text>Quantity: {grape.quantity_kg} kg</Card.Text>
                            <Card.Text>Quality: {grape.quality}</Card.Text>
                            <Button
                              variant="primary"
                              onClick={() => {
                                setSelectedGrapeToProcess(grape);
                                setShowProcessGrapesModal(true);
                              }}
                            >
                              Process
                            </Button>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}

                <h5 className="mt-4">Must:</h5>
                {player.winery?.must_in_production.length === 0 ? (
                  <Card.Text>No must in production.</Card.Text>
                ) : (
                  <Row xs={1} md={2} lg={3} className="g-4">
                    {player.winery?.must_in_production.map((must, index) => (
                      <Col key={index}>
                        <Card className="h-100 bg-secondary text-white">
                          <Card.Body>
                            <Card.Title>{must.varietal} ({must.vintage})</Card.Title>
                            <Card.Text>Quantity: {must.quantity_kg} kg</Card.Text>
                            <Card.Text>Quality: {must.quality}</Card.Text>
                            <Button
                              variant="success"
                              onClick={() => {
                                setSelectedMustToFerment(must);
                                setShowStartFermentationModal(true);
                              }}
                            >
                              Start Fermentation
                            </Button>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}

                <h5 className="mt-4">Wines Fermenting:</h5>
                {player.winery?.wines_fermenting.length === 0 ? (
                    <Card.Text>No wines fermenting.</Card.Text>
                ) : (
                    <Row xs={1} md={2} lg={3} className="g-4">
                        {player.winery?.wines_fermenting.map((wine, index) => (
                            <Col key={index}>
                                <Card className="h-100 bg-secondary text-white">
                                    <Card.Body>
                                        <Card.Title>{wine.varietal} ({wine.vintage})</Card.Title>
                                        <Card.Text>Vessel: {wine.vessel_type}</Card.Text>
                                        <Card.Text>Fermentation Progress: {wine.fermentation_progress}%</Card.Text>
                                        <Card.Text>Maceration Actions: {wine.maceration_actions_taken}</Card.Text>
                                        {grapeCharacteristics[wine.varietal as keyof typeof grapeCharacteristics]?.color === 'red' && (
                                            <Button
                                                variant="info"
                                                onClick={() => handlePerformMaceration(player.winery.wines_fermenting.findIndex(w => w.id === wine.id))}
                                                disabled={loading}
                                            >
                                                Perform Maceration
                                            </Button>
                                        )}
                                    </Card.Body>
                                </Card>
                            </Col>
                        ))}
                    </Row>
                )}

                <h5 className="mt-4">Wines Aging:</h5>
                {player.winery?.wines_aging.length === 0 ? (
                    <Card.Text>No wines aging.</Card.Text>
                ) : (
                    <Row xs={1} md={2} lg={3} className="g-4">
                        {player.winery?.wines_aging.map((wine, index) => (
                            <Col key={index}>
                                <Card className="h-100 bg-secondary text-white">
                                    <Card.Body>
                                        <Card.Title>{wine.varietal} ({wine.vintage})</Card.Title>
                                        <Card.Text>Vessel: {wine.vessel_type}</Card.Text>
                                        <Card.Text>Aging Progress: {wine.aging_progress}/{wine.aging_duration} months</Card.Text>
                                        {wine.aging_progress >= wine.aging_duration && (
                                            <Button
                                                variant="primary"
                                                onClick={() => {
                                                    setSelectedWineToBottle(wine);
                                                    setShowBottleWineModal(true);
                                                }}
                                                disabled={loading}
                                            >
                                                Bottle
                                            </Button>
                                        )}
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
                        <Card className="h-100 bg-secondary text-white">
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

      {/* Buy Vineyard Modal */}
      <Modal show={showBuyVineyardModal} onHide={() => setShowBuyVineyardModal(false)} centered dialogClassName="modal-dark">
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Buy New Vineyard</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-white">
          {buyVineyardError && <Alert variant="danger">{buyVineyardError}</Alert>}
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Vineyard Type</Form.Label>
              <Form.Control
                as="select"
                onChange={(e) => {
                  const [region, varietal] = e.target.value.split("|");
                  setSelectedVineyardToBuy({ ...regions[region as keyof typeof regions], varietal, region, cost: regions[region as keyof typeof regions].base_cost + Math.floor(Math.random() * 10000) - 5000 });
                }}
                className="bg-secondary text-white border-secondary"
              >
                <option value="">-- Select --</option>
                {Object.entries(regions).map(([regionName, regionData]) => (
                  (regionData as any).grape_varietals.map((varietal: string) => (
                    <option key={`${regionName}-${varietal}`} value={`${regionName}|${varietal}`}>
                      {varietal} from {regionName} (Est. Cost: ${((regionData as any).base_cost + Math.floor(Math.random() * 10000) - 5000).toLocaleString()})
                    </option>
                  ))
                ))}
              </Form.Control>
            </Form.Group>
            {selectedVineyardToBuy && (
              <Form.Group className="mb-3">
                <Form.Label>Vineyard Name</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter a name for your new vineyard"
                  value={newVineyardName}
                  onChange={(e) => setNewVineyardName(e.target.value)}
                  required
                  className="bg-secondary text-white border-secondary"
                />
                <Form.Text className="text-muted">
                  Cost: ${selectedVineyardToBuy.cost?.toLocaleString() || 'N/A'}
                </Form.Text>
              </Form.Group>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark border-top border-secondary">
          <Button variant="secondary" onClick={() => setShowBuyVineyardModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleBuyVineyard} disabled={loading || !selectedVineyardToBuy || !newVineyardName}>
            Buy Vineyard
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Buy Vessel Modal */}
      <Modal show={showBuyVesselModal} onHide={() => setShowBuyVesselModal(false)} centered dialogClassName="modal-dark">
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Buy New Vessel</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-white">
          {buyVesselError && <Alert variant="danger">{buyVesselError}</Alert>}
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Vessel Type</Form.Label>
              <Form.Control
                as="select"
                onChange={(e) => {
                  setSelectedVesselToBuy({ name: e.target.value, ...vesselTypes[e.target.value as keyof typeof vesselTypes] });
                }}
                className="bg-secondary text-white border-secondary"
              >
                <option value="">-- Select --</option>
                {Object.entries(vesselTypes).map(([vesselName, vesselData]) => (
                  <option key={vesselName} value={vesselName}>
                    {vesselName} (Capacity: {(vesselData as any).capacity}L, Cost: ${(vesselData as any).cost.toLocaleString()})
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark border-top border-secondary">
          <Button variant="secondary" onClick={() => setShowBuyVesselModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleBuyVessel} disabled={loading || !selectedVesselToBuy}>
            Buy Vessel
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Process Grapes Modal */}
      <Modal show={showProcessGrapesModal} onHide={() => setShowProcessGrapesModal(false)} centered dialogClassName="modal-dark">
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Process Grapes</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-white">
          {processGrapesError && <Alert variant="danger">{processGrapesError}</Alert>}
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Sort Grapes?</Form.Label>
              <Form.Control as="select" value={sortChoice} onChange={(e) => setSortChoice(e.target.value)} className="bg-secondary text-white border-secondary">
                <option value="no">No</option>
                <option value="yes">Yes (Cost: ${((selectedGrapeToProcess?.quantity_kg || 0) / 100 * 100).toFixed(2)})</option>
              </Form.Control>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Destem/Crush Method</Form.Label>
              <Form.Control as="select" value={destemCrushMethod} onChange={(e) => setDestemCrushMethod(e.target.value)} className="bg-secondary text-white border-secondary">
                <option value="Destemmed/Crushed">Destemmed/Crushed</option>
                <option value="Partial Destem">Partial Destem</option>
                <option value="Whole Cluster">Whole Cluster</option>
              </Form.Control>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark border-top border-secondary">
          <Button variant="secondary" onClick={() => setShowProcessGrapesModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleProcessGrapes} disabled={loading}>
            Process Grapes
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Start Fermentation Modal */}
      <Modal show={showStartFermentationModal} onHide={() => setShowStartFermentationModal(false)} centered dialogClassName="modal-dark">
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Start Fermentation</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-white">
          {startFermentationError && <Alert variant="danger">{startFermentationError}</Alert>}
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Select Fermentation Vessel</Form.Label>
              <Form.Control
                as="select"
                onChange={(e) => setSelectedVesselForFermentation(parseInt(e.target.value))}
                className="bg-secondary text-white border-secondary"
              >
                <option value="">-- Select an available vessel --</option>
                {vesselTypes && gameState?.player.winery.vessels.map((vessel, index) => (
                  !vessel.in_use && (vesselTypes[vessel.type as keyof typeof vesselTypes]?.type.includes("fermentation")) &&
                  <option key={index} value={index}>
                    {vessel.type} (Capacity: {vessel.capacity}L)
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark border-top border-secondary">
          <Button variant="secondary" onClick={() => setShowStartFermentationModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleStartFermentation} disabled={loading || selectedVesselForFermentation === null}>
            Start Fermentation
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Bottle Wine Modal */}
      <Modal show={showBottleWineModal} onHide={() => setShowBottleWineModal(false)} centered dialogClassName="modal-dark">
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Bottle Wine</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-dark text-white">
          {bottleWineError && <Alert variant="danger">{bottleWineError}</Alert>}
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Wine Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter a name for your wine"
                value={newWineName}
                onChange={(e) => setNewWineName(e.target.value)}
                required
                className="bg-secondary text-white border-secondary"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark border-top border-secondary">
          <Button variant="secondary" onClick={() => setShowBottleWineModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleBottleWine} disabled={loading || !newWineName}>
            Bottle Wine
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
