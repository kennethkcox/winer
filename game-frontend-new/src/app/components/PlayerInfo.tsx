'use client'

import { Box, Heading, Text } from "@chakra-ui/react";
import { Player } from "../page";

interface PlayerInfoProps {
  player: Player;
}

export const PlayerInfo = ({ player }: PlayerInfoProps) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" mb={6} bg="gray.700">
      <Heading fontSize="xl" mb={4}>Player Info</Heading>
      <Text><strong>Name:</strong> {player.name}</Text>
      <Text><strong>Vineyards Owned:</strong> {player.vineyards.length}</Text>
      <Text><strong>Winery Vessels:</strong> {player.winery?.vessels.length || 0}</Text>
    </Box>
  );
};
