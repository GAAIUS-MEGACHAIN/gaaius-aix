import React from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { theme } from '../theme';
import { AuthProvider } from '../context/AuthContext';
import { TeamsProvider } from '../context/TeamsContext';
import { TasksProvider } from '../context/TasksContext';
import { FilesProvider } from '../context/FilesContext';

function MyApp({ Component, pageProps }) {
  return (
    <ChakraProvider theme={theme}>
      <AuthProvider>
        <TeamsProvider>
          <TasksProvider>
            <FilesProvider>
              <Component {...pageProps} />
            </FilesProvider>
          </TasksProvider>
        </TeamsProvider>
      </AuthProvider>
    </ChakraProvider>
  );
}

export default MyApp;