'use client'

import {
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalFooter, ModalBody, ModalCloseButton,
  Button, FormControl, FormLabel, Input, Text, Alert, AlertIcon, NumberInput, NumberInputField, NumberInputStepper, NumberIncrementStepper, NumberDecrementStepper
} from "@chakra-ui/react";
import { Wine } from "../page";
import { useState } from "react";

interface SellWineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSell: (wineId: number, bottles: number) => void;
  wineToSell: Wine | null;
  loading: boolean;
}

export const SellWineModal = ({ isOpen, onClose, onSell, wineToSell, loading }: SellWineModalProps) => {
  const [bottles, setBottles] = useState(1);

  if (!wineToSell) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent bg="gray.700" color="white">
        <ModalHeader>Sell {wineToSell.name}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Text mb={4}>You have {wineToSell.bottles} bottles available.</Text>
          <FormControl isRequired>
            <FormLabel>Number of bottles to sell</FormLabel>
            <NumberInput
              defaultValue={1}
              min={1}
              max={wineToSell.bottles}
              onChange={(valueString) => setBottles(parseInt(valueString))}
              value={bottles}
            >
              <NumberInputField />
              <NumberInputStepper>
                <NumberIncrementStepper />
                <NumberDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
          </FormControl>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="teal"
            onClick={() => onSell(wineToSell.id, bottles)}
            isLoading={loading}
          >
            Sell
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
