import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Gamepad2, Trophy, Users, Award, Plus } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #facc15 0%, #ea580c 100%);
  border-radius: 12px;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  font-size: 28px;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: white;

  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }
`;

const Button = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  width: 100%;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const StatRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin: 8px 0;
`;

const GamingTab = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const token = localStorage.getItem('gaaius_token');

  useEffect(() => {
    fetchGames();
  }, []);

  const fetchGames = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/v1/gaming/leaderboards`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGames(response.data.games || []);
    } catch (error) {
      console.error('Error fetching games:', error);
    } finally {
      setLoading(false);
    }
  };

  const mockGames = [
    {
      game_id: '1',
      name: 'Arcade Quest',
      players: 1234,
      topScore: 95420,
      achievements: 12
    },
    {
      game_id: '2',
      name: 'Challenge Master',
      players: 892,
      topScore: 87650,
      achievements: 8
    },
    {
      game_id: '3',
      name: 'Speed Runner',
      players: 1567,
      topScore: 102340,
      achievements: 15
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <Gamepad2 size={32} />
          Gaming Platform
        </Title>
      </Header>

      <GridContainer>
        {games.length === 0 ? 
          mockGames.map((game) => (
            <Card key={game.game_id}>
              <h3 style={{ margin: '0 0 10px 0' }}>{game.name}</h3>
              <StatRow>
                <span>
                  <Users size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Players: {game.players}
                </span>
              </StatRow>
              <StatRow>
                <span>
                  <Trophy size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Top Score: {game.topScore}
                </span>
              </StatRow>
              <StatRow>
                <span>
                  <Award size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Achievements: {game.achievements}
                </span>
              </StatRow>
              <Button style={{ marginTop: '15px' }}>Play Game</Button>
              <Button style={{ marginTop: '10px' }}>View Leaderboard</Button>
            </Card>
          ))
        :
          games.map((game) => (
            <Card key={game.game_id}>
              <h3 style={{ margin: '0 0 10px 0' }}>{game.name}</h3>
              <StatRow>
                <span>
                  <Users size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Players: {game.players}
                </span>
              </StatRow>
              <Button style={{ marginTop: '15px' }}>Play Game</Button>
            </Card>
          ))
        }
      </GridContainer>
    </Container>
  );
};

export default GamingTab;
