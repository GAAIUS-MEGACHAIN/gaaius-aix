import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { useTeams } from '../hooks/useTeams';

interface TeamListProps {
  children: React.ReactNode;
}

const TeamList: React.FC<TeamListProps> = ({ children }) => {
  const { teams } = useTeams();

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold">
        Teams
      </Text>
      <Flex flexWrap="wrap" justify="space-between" mt="4">
        {teams.map((team) => (
          <Box key={team.id} bg="gray.100" p="4" borderRadius="md" mb="4" w="calc(33.33% - 16px)">
            <Text fontSize="md" fontWeight="bold">
              {team.name}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {team.description}
            </Text>
          </Box>
        ))}
      </Flex>
    </Box>
  );
};

export default TeamList;