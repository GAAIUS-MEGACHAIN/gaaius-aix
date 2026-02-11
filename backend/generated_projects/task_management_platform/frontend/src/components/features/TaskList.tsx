import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { useTasks } from '../hooks/useTasks';

interface TaskListProps {
  children: React.ReactNode;
}

const TaskList: React.FC<TaskListProps> = ({ children }) => {
  const { tasks } = useTasks();

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold">
        Tasks
      </Text>
      <Flex flexWrap="wrap" justify="space-between" mt="4">
        {tasks.map((task) => (
          <Box key={task.id} bg="gray.100" p="4" borderRadius="md" mb="4" w="calc(33.33% - 16px)">
            <Text fontSize="md" fontWeight="bold">
              {task.name}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {task.description}
            </Text>
          </Box>
        ))}
      </Flex>
    </Box>
  );
};

export default TaskList;