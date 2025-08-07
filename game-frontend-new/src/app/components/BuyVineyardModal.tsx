'use client'

import {
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  Button, FormControl, FormLabel, Input, Select, Text, Alert, AlertIcon
} from "@chakra-ui/react";

interface BuyVineyardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBuy: () => void;
  regions: any;
  selectedVineyardToBuy: any;
  setSelectedVineyardToBuy: (value: any) => void;
  newVineyardName: string;
  setNewVineyardName: (value: string) => void;
  buyVineyardError: string | null;
  loading: boolean;
}

export const BuyVineyardModal = ({
  isOpen, onClose, onBuy, regions, selectedVineyardToBuy,
  setSelectedVineyardToBuy, newVineyardName, setNewVineyardName,
  buyVineyardError, loading
}: BuyVineyardModalProps) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent bg="gray.700" color="white">
        <ModalHeader>Buy New Vineyard</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {buyVineyardError && <Alert status="error" mb={4}><AlertIcon />{buyVineyardError}</Alert>}
          <FormControl isRequired mb={4}>
            <FormLabel>Select Vineyard Type</FormLabel>
            <Select
              placeholder="-- Select --"
              onChange={(e) => {
                if (!e.target.value) {
                  setSelectedVineyardToBuy(null);
                  return;
                }
                const [region, varietal] = e.target.value.split("|");
                setSelectedVineyardToBuy({ region, varietal });
              }}
            >
              {Object.entries(regions).map(([regionName, regionData]: [string, any]) => (
                (regionData as any).grape_varietals.map((varietal: string) => (
                  <option key={`${regionName}-${varietal}`} value={`${regionName}|${varietal}`} style={{ backgroundColor: '#2D3748' }}>
                    {varietal} from {regionName} (Base Cost: ${regionData.base_cost.toLocaleString()})
                  </option>
                ))
              ))}
            </Select>
          </FormControl>
          {selectedVineyardToBuy && (
            <FormControl isRequired>
              <FormLabel>Vineyard Name</FormLabel>
              <Input
                placeholder="Enter a name for your new vineyard"
                value={newVineyardName}
                onChange={(e) => setNewVineyardName(e.target.value)}
              />
              <Text fontSize="sm" color="gray.400" mt={1}>
                The final cost will be determined upon purchase.
              </Text>
            </FormControl>
          )}
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="teal"
            onClick={onBuy}
            isLoading={loading}
            isDisabled={!selectedVineyardToBuy || !newVineyardName}
          >
            Buy Vineyard
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
