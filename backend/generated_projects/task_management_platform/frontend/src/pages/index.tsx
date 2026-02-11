import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { useAuth } from '../hooks/useAuth';

interface IndexProps {
  children: React.ReactNode;
}

const Index: React.FC<IndexProps> = ({ children }) => {
  const { user } = useAuth();

  return (
    <Box>
      <Flex justify="center" align="center" h="100vh">
        <Text fontSize="lg" fontWeight="bold">
          TaskHub
        </Text>
        {user ? (
          <Text fontSize="sm" color="gray.500">
            Welcome, {user.name}!
          </Text>
        ) : (
          <Text fontSize="sm" color="gray.500">
            Please login to access TaskHub
          </Text>
        )}
      </Flex>
    </Box>
  );
};

export default Index;