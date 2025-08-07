'use client'

import { Box, Heading, Text, Button, SimpleGrid } from "@chakra-ui/react";
import { Player } from "../page";
import { VineyardCard } from "./VineyardCard";

interface VineyardsProps {
  player: Player;
  onTend: (name: string) => void;
  onHarvest: (name: string) => void;
  onOpenBuyVineyard: () => void;
  loading: boolean;
}

export const Vineyards = ({ player, onTend, onHarvest, onOpenBuyVineyard, loading }: VineyardsProps) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={6} bg="gray.700">
      <Heading fontSize="xl" mb={4}>Your Vineyards</Heading>
      {player.vineyards.length === 0 ? (
        <Text>You don&apos;t own any vineyards yet. Time to buy one!</Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {player.vineyards.map((vineyard, index) => (
            <VineyardCard
              key={index}
              vineyard={vineyard}
              onTend={onTend}
              onHarvest={onHarvest}
              loading={loading}
            />
          ))}
        </SimpleGrid>
      )}
      <Button colorScheme="teal" mt={6} onClick={onOpenBuyVineyard}>
        Buy New Vineyard
      </Button>
    </Box>
  );
};
