import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { useAuth } from '../hooks/useAuth';

interface SidebarProps {
  children: React.ReactNode;
}

const Sidebar: React.FC<SidebarProps> = ({ children }) => {
  const { user } = useAuth();

  return (
    <Box
      bg="gray.100"
      w="250px"
      h="100vh"
      pos="fixed"
      top="0"
      left="0"
      p="4"
      borderRight="1px solid #e5e5e5"
    >
      <Flex justify="space-between" align="center" mb="4">
        <Text fontSize="lg" fontWeight="bold">
          TaskHub
        </Text>
        <Text fontSize="sm" color="gray.500">
          {user?.name}
        </Text>
      </Flex>
      {children}
    </Box>
  );
};

export default Sidebar;