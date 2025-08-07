'use client'

import { Box, Heading, Text, SimpleGrid } from "@chakra-ui/react";
import { Player } from "../page";

import { Button } from "@chakra-ui/react";
import { Wine } from "../page";

interface InventoryProps {
  player: Player;
  onOpenSellWine: (wine: Wine) => void;
}

export const Inventory = ({ player, onOpenSellWine }: InventoryProps) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={6} bg="gray.700">
      <Heading fontSize="xl" mb={4}>Inventory</Heading>
      <Heading fontSize="lg" mt={4} mb={2}>Grapes:</Heading>
      {player.grapes_inventory.length === 0 ? (
        <Text>No grapes in inventory.</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {player.grapes_inventory.map((grape, index) => (
            <Box key={index} p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="gray.600">
              <Heading fontSize="lg">{grape.varietal} ({grape.vintage})</Heading>
              <Text>Quantity: {grape.quantity_kg} kg</Text>
              <Text>Quality: {grape.quality}</Text>
            </Box>
          ))}
        </SimpleGrid>
      )}

      <Heading fontSize="lg" mt={4} mb={2}>Bottled Wines:</Heading>
      {player.bottled_wines.length === 0 ? (
        <Text>No bottled wines yet.</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {player.bottled_wines.map((wine, index) => (
            <Box key={index} p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="gray.600">
              <Heading fontSize="lg">{wine.name} ({wine.vintage})</Heading>
              <Text>Varietal: {wine.varietal}</Text>
              <Text>Style: {wine.style}</Text>
              <Text>Quality: {wine.quality}</Text>
              <Text>Bottles: {wine.bottles}</Text>
              <Button mt={4} colorScheme="purple" onClick={() => onOpenSellWine(wine)}>Sell</Button>
            </Box>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
};
