import React from 'react';
import styled from 'styled-components';
import { Calendar, Plus, Eye, DollarSign } from 'lucide-react';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #6366f1 0%, #312e81 100%);
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

const EventsTab = () => {
  const mockEvents = [
    {
      event_id: '1',
      name: 'Virtual Conference 2024',
      date: 'Feb 15, 2024',
      attendees: 2341,
      revenue: 23410
    },
    {
      event_id: '2',
      name: 'Webinar: Future of Tech',
      date: 'Jan 28, 2024',
      attendees: 456,
      revenue: 4560
    },
    {
      event_id: '3',
      name: 'Networking Mixer',
      date: 'Feb 20, 2024',
      attendees: 189,
      revenue: 1890
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <Calendar size={32} />
          Events & Ticketing
        </Title>
        <Button style={{ width: 'auto' }}>
          <Plus size={16} style={{ display: 'inline', marginRight: '5px' }} />
          Create Event
        </Button>
      </Header>

      <GridContainer>
        {mockEvents.map((event) => (
          <Card key={event.event_id}>
            <h3 style={{ margin: '0 0 10px 0' }}>{event.name}</h3>
            <StatRow>
              <span>📅 {event.date}</span>
            </StatRow>
            <StatRow>
              <span>
                <Eye size={16} style={{ display: 'inline', marginRight: '5px' }} />
                Attendees: {event.attendees}
              </span>
            </StatRow>
            <StatRow style={{ marginTop: '15px', fontSize: '15px', fontWeight: 'bold' }}>
              <span>
                <DollarSign size={16} style={{ display: 'inline', marginRight: '5px' }} />
                ${event.revenue}
              </span>
            </StatRow>
            <Button style={{ marginTop: '15px' }}>Manage Event</Button>
            <Button style={{ marginTop: '10px' }}>View Tickets</Button>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default EventsTab;
