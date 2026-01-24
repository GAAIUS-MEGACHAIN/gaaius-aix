import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';
import { useFiles } from '../hooks/useFiles';

interface FileListProps {
  children: React.ReactNode;
}

const FileList: React.FC<FileListProps> = ({ children }) => {
  const { files } = useFiles();

  return (
    <Box>
      <Text fontSize="lg" fontWeight="bold">
        Files
      </Text>
      <Flex flexWrap="wrap" justify="space-between" mt="4">
        {files.map((file) => (
          <Box key={file.id} bg="gray.100" p="4" borderRadius="md" mb="4" w="calc(33.33% - 16px)">
            <Text fontSize="md" fontWeight="bold">
              {file.name}
            </Text>
            <Text fontSize="sm" color="gray.500">
              {file.type}
            </Text>
          </Box>
        ))}
      </Flex>
    </Box>
  );
};

export default FileList;