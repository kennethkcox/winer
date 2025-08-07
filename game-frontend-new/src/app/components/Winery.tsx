'use client'

import { Box, Heading, Text, Button, SimpleGrid } from "@chakra-ui/react";
import { Player } from "../page";

interface WineryProps {
  player: Player;
  onOpenBuyVessel: () => void;
}

export const Winery = ({ player, onOpenBuyVessel }: WineryProps) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={6} bg="gray.700">
      <Heading fontSize="xl" mb={4}>Your Winery</Heading>
      <Text>Winery Name: {player.winery?.name || "N/A"}</Text>
      <Heading fontSize="lg" mt={4} mb={2}>Vessels:</Heading>
      {player.winery?.vessels.length === 0 ? (
        <Text>No vessels in your winery yet.</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {player.winery?.vessels.map((vessel, index) => (
            <Box key={index} p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="gray.600">
              <Heading fontSize="lg">{vessel.type}</Heading>
              <Text>Capacity: {vessel.capacity}L</Text>
              <Text>In Use: {vessel.in_use ? "Yes" : "No"}</Text>
            </Box>
          ))}
        </SimpleGrid>
      )}
      <Button colorScheme="teal" mt={6} onClick={onOpenBuyVessel}>
        Buy New Vessel
      </Button>
    </Box>
  );
};
