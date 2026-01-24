import { createContext, useState } from 'react';

interface TasksContextProps {
  children: React.ReactNode;
}

interface TasksContextType {
  tasks: any[];
  getTasks: () => void;
  addTask: (task: any) => void;
  removeTask: (taskId: string) => void;
}

const TasksContext = createContext<TasksContextType | null>(null);

const TasksProvider: React.FC<TasksContextProps> = ({