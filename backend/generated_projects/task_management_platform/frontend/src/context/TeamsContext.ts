import { createContext, useState } from 'react';

interface TeamsContextProps {
  children: React.ReactNode;
}

interface TeamsContextType {
  teams: any[];
  getTeams: () => void;
  addTeam: (team: any) => void;
  removeTeam: (teamId: string) => void;
}

const TeamsContext = createContext<TeamsContextType | null>(null);

const TeamsProvider: React.FC<TeamsContextProps> = ({ children }) => {
  const [teams, setTeams] = useState([]);

  const getTeams = () => {
    // fetch teams from API
  };

  const addTeam = (team: any) => {
    setTeams([...teams, team]);
  };

  const removeTeam = (teamId: string) => {
    setTeams(teams.filter((team) => team.id !== teamId));
  };

  return (
    <TeamsContext.Provider value={{ teams, getTeams, addTeam, removeTeam }}>
      {children}
    </TeamsContext.Provider>
  );
};

export { TeamsProvider, TeamsContext };