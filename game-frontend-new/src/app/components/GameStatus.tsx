'use client'

import { Box, Heading, Text, Button } from "@chakra-ui/react";
import { GameState, Player } from "../page";

interface GameStatusProps {
  gameState: GameState;
  player: Player;
  onAdvanceMonth: () => void;
  loading: boolean;
}

export const GameStatus = ({ gameState, player, onAdvanceMonth, loading }: GameStatusProps) => {
  const { current_year, current_month_index, months } = gameState;

  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={6} bg="gray.700">
      <Heading fontSize="xl" mb={4}>Game Status</Heading>
      <Text><strong>Date:</strong> {months[current_month_index]}, {current_year}</Text>
      <Text><strong>Money:</strong> ${player.money.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</Text>
      <Text><strong>Reputation:</strong> {player.reputation}/100</Text>
      <Text><strong>Grapes:</strong> {(player.grapes_inventory || []).reduce((sum, g) => sum + g.quantity_kg, 0)} kg</Text>
      <Text><strong>Bottled Wine:</strong> {(player.bottled_wines || []).reduce((sum, w) => sum + w.bottles, 0)} bottles</Text>
      <Button colorScheme="green" mt={4} onClick={onAdvanceMonth} isLoading={loading}>
        Advance Month
      </Button>
    </Box>
  );
};
