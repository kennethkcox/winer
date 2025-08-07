"use client";

import { useState, useEffect } from "react";
import {
  Box, Container, Flex, Heading, Text, Button, SimpleGrid,
  FormControl, FormLabel, Input, Select, Alert, AlertIcon,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  useDisclosure,
  Spinner
} from "@chakra-ui/react";
import toast, { Toaster } from 'react-hot-toast';

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
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [token, setToken] = useState<string | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);

  const [regions, setRegions] = useState<any>({});
  const [vesselTypes, setVesselTypes] = useState<any>({});

  const { isOpen: isBuyVineyardOpen, onOpen: onBuyVineyardOpen, onClose: onBuyVineyardClose } = useDisclosure();
  const [selectedVineyardToBuy, setSelectedVineyardToBuy] = useState<any>(null);
  const [newVineyardName, setNewVineyardName] = useState<string>("");
  const [buyVineyardError, setBuyVineyardError] = useState<string | null>(null);

  const { isOpen: isBuyVesselOpen, onOpen: onBuyVesselOpen, onClose: onBuyVesselClose } = useDisclosure();
  const [selectedVesselToBuy, setSelectedVesselToBuy] = useState<any>(null);
  const [buyVesselError, setBuyVesselError] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("accessToken");
    if (storedToken) {
      setToken(storedToken);
      fetchInitialData(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchInitialData = async (authToken: string) => {
    setLoading(true);
    try {
      const [regionsRes, vesselTypesRes, gameStateRes] = await Promise.all([
        fetch(`${BACKEND_URL}/game_data/regions`, { headers: { "Authorization": `Bearer ${authToken}` } }),
        fetch(`${BACKEND_URL}/game_data/vessel_types`, { headers: { "Authorization": `Bearer ${authToken}` } }),
        fetch(`${BACKEND_URL}/`, { headers: { "Authorization": `Bearer ${authToken}` } }),
      ]);

      if (!regionsRes.ok || !vesselTypesRes.ok || !gameStateRes.ok) {
        if (gameStateRes.status === 401) {
          setLoginError("Unauthorized. Please log in.");
          setToken(null);
          localStorage.removeItem("accessToken");
        }
        throw new Error(`HTTP error! Failed to fetch initial data.`);
      }

      const regionsData = await regionsRes.json();
      const vesselTypesData = await vesselTypesRes.json();
      const gameStateData = await gameStateRes.json();

      setRegions(regionsData);
      setVesselTypes(vesselTypesData);
      setGameState(gameStateData);

    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchGameState = async (authToken: string | null = token) => {
    setLoading(true);
    setError(null);
    try {
      const headers: HeadersInit = {};
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }
      const response = await fetch(`${BACKEND_URL}/`, {
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
      const response = await fetch(`${BACKEND_URL}/advance_month`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (!response.ok) {
        if (response.status === 401) {
          setLoginError("Unauthorized. Please log in.");
          setToken(null);
          localStorage.removeItem("accessToken");
        }
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      setGameState(data);
      toast.success("Advanced to the next month!");
      if (data.event_message) {
        toast.info(data.event_message, { duration: 6000 });
      }
    } catch (e: any) {
      toast.error(`Failed to advance month: ${e.message}`);
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

      const response = await fetch(`${BACKEND_URL}/token`, {
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
      await fetchInitialData(data.access_token); // Fetch all initial data
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
    setRegions({});
    setVesselTypes({});
    setLoading(false);
  };

  const handleBuyVineyard = async () => {
    if (!selectedVineyardToBuy || !newVineyardName) return;
    setLoading(true);
    const toastId = toast.loading("Purchasing vineyard...");
    try {
      const response = await fetch(`${BACKEND_URL}/buy_vineyard`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          region: selectedVineyardToBuy.region,
          varietal: selectedVineyardToBuy.varietal,
          vineyard_name: newVineyardName,
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      // Optimistic UI update
      setGameState(prev => {
        if (!prev) return null;
        const newVineyards = [...prev.player.vineyards, data.new_vineyard];
        const newPlayer = { ...prev.player, money: data.updated_money, vineyards: newVineyards };
        return { ...prev, player: newPlayer };
      });
      onBuyVineyardClose();
      setNewVineyardName("");
      setSelectedVineyardToBuy(null);
      toast.success(`Vineyard '${data.new_vineyard.name}' purchased!`, { id: toastId });
    } catch (e: any) {
      toast.error(`Failed to buy vineyard: ${e.message}`, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  const handleTendVineyard = async (vineyardName: string) => {
    setLoading(true);
    const toastId = toast.loading(`Tending ${vineyardName}...`);
    try {
      const response = await fetch(`${BACKEND_URL}/tend_vineyard`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vineyard_name: vineyardName }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
      toast.success(`Tended ${vineyardName}!`, { id: toastId });
    } catch (e: any) {
      toast.error(`Failed to tend vineyard: ${e.message}`, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  const handleHarvestGrapes = async (vineyardName: string) => {
    setLoading(true);
    const toastId = toast.loading(`Harvesting from ${vineyardName}...`);
    try {
      const response = await fetch(`${BACKEND_URL}/harvest_grapes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vineyard_name: vineyardName }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState();
      toast.success(`Harvested grapes from ${vineyardName}!`, { id: toastId });
    } catch (e: any)
      toast.error(`Failed to harvest: ${e.message}`, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  const handleBuyVessel = async () => {
    if (!selectedVesselToBuy) return;
    setLoading(true);
    const toastId = toast.loading(`Buying ${selectedVesselToBuy.name}...`);
    try {
      const response = await fetch(`${BACKEND_URL}/buy_vessel`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ vessel_type_name: selectedVesselToBuy.name }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      await fetchGameState(); // Refresh game state
      onBuyVesselClose();
      setSelectedVesselToBuy(null);
      toast.success(`Vessel '${selectedVesselToBuy.name}' purchased!`, { id: toastId });
    } catch (e: any) {
      toast.error(`Failed to buy vessel: ${e.message}`, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  if (loading && !gameState) {
    return (
      <Flex justify="center" align="center" height="100vh">
        <Spinner size="xl" />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex justify="center" align="center" height="100vh">
        <Alert status="error">
          <AlertIcon />
          <Text>{error}</Text>
        </Alert>
      </Flex>
    );
  }

  if (!token || !gameState) {
    return (
      <Flex justify="center" align="center" height="100vh" bg="gray.800">
        <Box p={8} maxW="md" borderWidth={1} borderRadius={8} boxShadow="lg" bg="gray.700" color="white">
          <Heading as="h1" size="lg" textAlign="center" mb={6}>Terroir & Time</Heading>
          {loginError && (
            <Alert status="error" mb={4}>
              <AlertIcon />
              {loginError}
            </Alert>
          )}
          <form onSubmit={handleLogin}>
            <FormControl isRequired mb={4}>
              <FormLabel>Username</FormLabel>
              <Input
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </FormControl>
            <FormControl isRequired mb={6}>
              <FormLabel>Password</Form.Label>
              <Input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </FormControl>
            <Button colorScheme="blue" type="submit" isLoading={loading} width="full">
              Login
            </Button>
          </form>
        </Box>
      </Flex>
    );
  }

  const { player, current_year, current_month_index, months } = gameState;

import { GameStatus } from "./components/GameStatus";
import { PlayerInfo } from "./components/PlayerInfo";
import { Vineyards } from "./components/Vineyards";
import { Winery } from "./components/Winery";
import { Inventory } from "./components/Inventory";
import { BuyVineyardModal } from "./components/BuyVineyardModal";
import { BuyVesselModal } from "./components/BuyVesselModal";
import { SellWineModal } from "./components/SellWineModal";
import { Wine } from "./page";

  const { isOpen: isSellWineOpen, onOpen: onSellWineOpen, onClose: onSellWineClose } = useDisclosure();
  const [wineToSell, setWineToSell] = useState<Wine | null>(null);

  const handleOpenSellWineModal = (wine: Wine) => {
    setWineToSell(wine);
    onSellWineOpen();
  };

  const handleSellWine = async (wineId: number, bottles: number) => {
    setLoading(true);
    const toastId = toast.loading(`Selling ${bottles} bottles...`);
    try {
      const response = await fetch(`${BACKEND_URL}/sell_wine`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ wine_id: wineId, bottles }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }
      // Optimistic UI update
      setGameState(prev => {
        if (!prev) return null;
        const newWines = prev.player.bottled_wines.map(w =>
          w.id === data.sold_wine_id ? { ...w, bottles: data.bottles_remaining } : w
        ).filter(w => w.bottles > 0);
        const newPlayer = { ...prev.player, money: data.updated_money, bottled_wines: newWines };
        return { ...prev, player: newPlayer };
      });
      onSellWineClose();
      toast.success("Wine sold!", { id: toastId });
    } catch (e: any) {
      toast.error(`Failed to sell wine: ${e.message}`, { id: toastId });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box bg="gray.800" color="white" minH="100vh">
      <Toaster position="top-center" reverseOrder={false} />
      <Flex as="nav" align="center" justify="space-between" wrap="wrap" padding="1.5rem" bg="gray.900">
        <Flex align="center" mr={5}>
          <Heading as="h1" size="lg" letterSpacing={"tighter"}>
            Terroir & Time
          </Heading>
        </Flex>
        <Button colorScheme="teal" onClick={handleLogout}>Logout</Button>
      </Flex>

      <Container maxW="container.xl" pt={8}>
        <Heading as="h2" size="xl" mb={6} textAlign="center">A Natural Winemaking Saga</Heading>

        <GameStatus
          gameState={gameState}
          player={player}
          onAdvanceMonth={handleAdvanceMonth}
          loading={loading}
        />

        <PlayerInfo player={player} />

        <Vineyards
          player={player}
          onTend={handleTendVineyard}
          onHarvest={handleHarvestGrapes}
          onOpenBuyVineyard={onBuyVineyardOpen}
          loading={loading}
        />

        <Winery
          player={player}
          onOpenBuyVessel={onBuyVesselOpen}
        />

        <Inventory player={player} onOpenSellWine={handleOpenSellWineModal} />

      </Container>

      <SellWineModal
        isOpen={isSellWineOpen}
        onClose={onSellWineClose}
        onSell={handleSellWine}
        wineToSell={wineToSell}
        loading={loading}
      />

      <BuyVineyardModal
        isOpen={isBuyVineyardOpen}
        onClose={onBuyVineyardClose}
        onBuy={handleBuyVineyard}
        regions={regions}
        selectedVineyardToBuy={selectedVineyardToBuy}
        setSelectedVineyardToBuy={setSelectedVineyardToBuy}
        newVineyardName={newVineyardName}
        setNewVineyardName={setNewVineyardName}
        buyVineyardError={buyVineyardError}
        loading={loading}
      />

      <BuyVesselModal
        isOpen={isBuyVesselOpen}
        onClose={onBuyVesselClose}
        onBuy={handleBuyVessel}
        vesselTypes={vesselTypes}
        selectedVesselToBuy={selectedVesselToBuy}
        setSelectedVesselToBuy={setSelectedVesselToBuy}
        buyVesselError={buyVesselError}
        loading={loading}
      />
    </Box>
  );
}
