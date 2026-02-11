import React from 'react';
import { Button as ChakraButton, ButtonProps as ChakraButtonProps } from '@chakra-ui/react';

interface ButtonProps extends ChakraButtonProps {
  variant?: 'solid' | 'outline' | 'link';
  colorScheme?: 'gray' | 'blue' | 'green' | 'yellow';
  size?: 'sm' | 'md' | 'lg';
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'solid', colorScheme = 'blue', size = 'md', ...props }) => {
  return (
    <ChakraButton
      variant={variant}
      colorScheme={colorScheme}
      size={size}
      {...props}
    >
      {children}
    </ChakraButton>
  );
};

export default Button;