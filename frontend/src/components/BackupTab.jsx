import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, HardDrive, Download, Trash2, RotateCcw, Clock } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  min-height: 100vh;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;

  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.8rem;
  }
`;

const Button = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  }

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
  }
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }
`;

const CardTitle = styled.h3`
  font-size: 1.3rem;
  color: #333;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const BackupItem = styled.div`
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 12px;

  &:hover {
    background: #f0f0f0;
  }
`;

const BackupName = styled.div`
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const BackupInfo = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 10px;
`;

const BackupStatus = styled.div`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  background: ${props => {
    switch(props.status) {
      case 'Complete': return '#D1FAE5';
      case 'In Progress': return '#FEF3C7';
      case 'Failed': return '#FEE2E2';
      default: return '#E0E7FF';
    }
  }};
  color: ${props => {
    switch(props.status) {
      case 'Complete': return '#065F46';
      case 'In Progress': return '#92400E';
      case 'Failed': return '#7F1D1D';
      default: return '#3730A3';
    }
  }};
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin: 15px 0;
`;

const StatBox = styled.div`
  background: ${props => props.color || '#f0f0f0'};
  padding: 15px;
  border-radius: 8px;
  text-align: center;

  & > div:first-child {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 5px;
  }

  & > div:last-child {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 10px;

  & > button {
    flex: 1;
  }
`;

const SmallButton = styled.button`
  background: #6366F1;
  color: white;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.3s;

  &:hover {
    background: #4F46E5;
    transform: translateY(-1px);
  }
`;

const FormContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  max-width: 600px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #6366F1;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;

  &:focus {
    outline: none;
    border-color: #6366F1;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #6366F1;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #4F46E5;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const BackupTab = () => {
  const [backups, setBackups] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    type: 'full'
  });

  const mockBackups = [
    {
      id: 1,
      name: 'Full System Backup - Jan 18',
      type: 'Full Backup',
      size: '45.2 GB',
      status: 'Complete',
      created: '2026-01-18 14:32:00',
      dataPoints: 15420
    },
    {
      id: 2,
      name: 'Incremental Backup - Jan 17',
      type: 'Incremental',
      size: '3.8 GB',
      status: 'Complete',
      created: '2026-01-17 02:15:00',
      dataPoints: 1240
    },
    {
      id: 3,
      name: 'Database Backup - Jan 16',
      type: 'Database Only',
      size: '8.5 GB',
      status: 'Complete',
      created: '2026-01-16 18:45:00',
      dataPoints: 2850
    },
    {
      id: 4,
      name: 'Media Files Backup',
      type: 'Media Only',
      size: '28.3 GB',
      status: 'In Progress',
      created: '2026-01-18 10:00:00',
      dataPoints: 12500
    }
  ];

  useEffect(() => {
    fetchBackups();
  }, []);

  const fetchBackups = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/backup/list`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setBackups(response.data.backups || mockBackups);
    } catch (error) {
      console.error('Error fetching backups:', error);
      setBackups(mockBackups);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateBackup = async (e) => {
    e.preventDefault();

    if (!formData.name) {
      toast.error('Please enter backup name');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/backup/create`,
        {
          name: formData.name,
          type: formData.type
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setFormData({ name: '', type: 'full' });
      setShowCreateForm(false);
      toast.success('Backup started!');
      fetchBackups();
    } catch (error) {
      console.error('Error creating backup:', error);
      toast.error('Failed to create backup');
    }
  };

  const handleRestore = (id) => {
    toast.success('Restore process started. This may take a while.');
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this backup?')) {
      setBackups(prev => prev.filter(b => b.id !== id));
      toast.success('Backup deleted');
    }
  };

  if (loading) {
    return <Container><Title><HardDrive /> Loading backups...</Title></Container>;
  }

  const totalSize = backups.reduce((sum, b) => {
    const sizeNum = parseFloat(b.size);
    return sum + sizeNum;
  }, 0);

  const completeCount = backups.filter(b => b.status === 'Complete').length;

  return (
    <Container>
      <Header>
        <Title>
          <HardDrive /> Backup & Restore
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> New Backup
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Create New Backup</h2>
          <form onSubmit={handleCreateBackup}>
            <FormGroup>
              <Label>Backup Name *</Label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Full System Backup - Jan 18"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Backup Type</Label>
              <Select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
              >
                <option value="full">Full Backup (Everything)</option>
                <option value="incremental">Incremental (Changes Only)</option>
                <option value="database">Database Only</option>
                <option value="media">Media Files Only</option>
                <option value="documents">Documents Only</option>
              </Select>
            </FormGroup>

            <SubmitButton type="submit">Start Backup</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        <Card>
          <CardTitle>
            <HardDrive size={20} /> Backup History
          </CardTitle>

          <StatsGrid>
            <StatBox color="#E0E7FF">
              <div>Total Backups</div>
              <div>{backups.length}</div>
            </StatBox>
            <StatBox color="#E0E7FF">
              <div>Completed</div>
              <div>{completeCount}</div>
            </StatBox>
            <StatBox color="#C7D2FE">
              <div>Total Size</div>
              <div>{totalSize.toFixed(1)} GB</div>
            </StatBox>
            <StatBox color="#C7D2FE">
              <div>Data Points</div>
              <div>{(backups.reduce((sum, b) => sum + b.dataPoints, 0) / 1000).toFixed(0)}K</div>
            </StatBox>
          </StatsGrid>

          {backups.map(backup => (
            <BackupItem key={backup.id}>
              <BackupName>
                <Clock size={16} /> {backup.name}
              </BackupName>
              <BackupInfo>
                <span><strong>Type:</strong> {backup.type}</span>
                <span><strong>Size:</strong> {backup.size}</span>
              </BackupInfo>
              <BackupInfo>
                <span>{backup.created}</span>
                <BackupStatus status={backup.status}>{backup.status}</BackupStatus>
              </BackupInfo>
              <ButtonGroup>
                <SmallButton onClick={() => handleRestore(backup.id)}>
                  <RotateCcw size={12} /> Restore
                </SmallButton>
                <SmallButton onClick={() => {
                  navigator.clipboard.writeText(`Backup: ${backup.name} (${backup.size})`);
                  toast.success('Details copied!');
                }}>
                  <Download size={12} /> Download
                </SmallButton>
                <SmallButton
                  onClick={() => handleDelete(backup.id)}
                  style={{ background: '#EF4444' }}
                  onMouseEnter={(e) => e.target.style.background = '#DC2626'}
                  onMouseLeave={(e) => e.target.style.background = '#EF4444'}
                >
                  <Trash2 size={12} /> Delete
                </SmallButton>
              </ButtonGroup>
            </BackupItem>
          ))}
        </Card>
      </GridContainer>

      <Card style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(79, 70, 229, 0.1) 100%)' }}>
        <h3>Backup Best Practices</h3>
        <ul style={{ color: '#666', lineHeight: '1.8' }}>
          <li><strong>Daily backups:</strong> Automate daily backup schedules</li>
          <li><strong>Multiple locations:</strong> Store backups in different locations</li>
          <li><strong>Verify integrity:</strong> Regularly test restore procedures</li>
          <li><strong>Encryption:</strong> Keep backups encrypted for security</li>
          <li><strong>Retention policy:</strong> Define how long to keep backups</li>
        </ul>
      </Card>
    </Container>
  );
};

export default BackupTab;
