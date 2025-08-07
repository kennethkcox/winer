'use client'

import {
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  Button, FormControl, FormLabel, Select, Alert, AlertIcon
} from "@chakra-ui/react";

interface BuyVesselModalProps {
  isOpen: boolean;
  onClose: () => void;
  onBuy: () => void;
  vesselTypes: any;
  selectedVesselToBuy: any;
  setSelectedVesselToBuy: (value: any) => void;
  buyVesselError: string | null;
  loading: boolean;
}

export const BuyVesselModal = ({
  isOpen, onClose, onBuy, vesselTypes, selectedVesselToBuy,
  setSelectedVesselToBuy, buyVesselError, loading
}: BuyVesselModalProps) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent bg="gray.700" color="white">
        <ModalHeader>Buy New Vessel</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {buyVesselError && <Alert status="error" mb={4}><AlertIcon />{buyVesselError}</Alert>}
          <FormControl isRequired>
            <FormLabel>Select Vessel Type</FormLabel>
            <Select
              placeholder="-- Select --"
              onChange={(e) => {
                if (!e.target.value) {
                  setSelectedVesselToBuy(null);
                  return;
                }
                setSelectedVesselToBuy({ name: e.target.value });
              }}
            >
              {Object.entries(vesselTypes).map(([vesselName, vesselData]: [string, any]) => (
                <option key={vesselName} value={vesselName} style={{ backgroundColor: '#2D3748' }}>
                  {vesselName} (Capacity: {vesselData.capacity}L, Cost: ${vesselData.cost.toLocaleString()})
                </option>
              ))}
            </Select>
          </FormControl>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="teal"
            onClick={onBuy}
            isLoading={loading}
            isDisabled={!selectedVesselToBuy}
          >
            Buy Vessel
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
