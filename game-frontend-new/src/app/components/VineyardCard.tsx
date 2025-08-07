'use client'

import { Box, Heading, Text, Button, Flex } from "@chakra-ui/react";
import { Vineyard } from "../page";

interface VineyardCardProps {
  vineyard: Vineyard;
  onTend: (name: string) => void;
  onHarvest: (name: string) => void;
  loading: boolean;
}

export const VineyardCard = ({ vineyard, onTend, onHarvest, loading }: VineyardCardProps) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="md" bg="gray.600">
      <Heading fontSize="lg">{vineyard.name} ({vineyard.varietal})</Heading>
      <Text>Region: {vineyard.region}</Text>
      <Text>Size: {vineyard.size_acres} acres</Text>
      <Text>Health: {vineyard.health}%</Text>
      <Text>Grapes Ready: {vineyard.grapes_ready ? "Yes" : "No"}</Text>
      <Text>Harvested This Year: {vineyard.harvested_this_year ? "Yes" : "No"}</Text>
      <Flex mt={4}>
        <Button
          colorScheme="blue"
          mr={3}
          onClick={() => onTend(vineyard.name)}
          isLoading={loading}
        >
          Tend
        </Button>
        <Button
          colorScheme="yellow"
          onClick={() => onHarvest(vineyard.name)}
          isDisabled={!vineyard.grapes_ready || vineyard.harvested_this_year}
          isLoading={loading}
        >
          Harvest
        </Button>
      </Flex>
    </Box>
  );
};
