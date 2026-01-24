import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Plus, QrCode, Copy, Download, BarChart3, Eye } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
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

const QRCodeBox = styled.div`
  background: #f0f0f0;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  margin: 15px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  font-size: 5rem;
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

const URLBox = styled.div`
  background: #f0f0f0;
  padding: 12px;
  border-radius: 8px;
  word-break: break-all;
  font-size: 0.85rem;
  color: #666;
  margin: 10px 0;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;

  & > button {
    flex: 1;
    min-width: 100px;
  }
`;

const SmallButton = styled.button`
  background: #3B82F6;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transition: all 0.3s;

  &:hover {
    background: #2563EB;
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
    border-color: #3B82F6;
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
    border-color: #3B82F6;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: #3B82F6;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    background: #2563EB;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const QRCodeTab = () => {
  const [qrCodes, setQRCodes] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    type: 'link'
  });

  const mockQRCodes = [
    {
      id: 1,
      name: 'Product Page QR',
      url: 'https://example.com/product/123',
      type: 'link',
      scans: 4523,
      uniqueScans: 1234,
      created: '2026-01-10',
      lastScanned: '2026-01-18'
    },
    {
      id: 2,
      name: 'Event Registration',
      url: 'https://example.com/event/register',
      type: 'link',
      scans: 8920,
      uniqueScans: 2340,
      created: '2025-12-15',
      lastScanned: '2026-01-18'
    },
    {
      id: 3,
      name: 'WiFi Network',
      url: 'WIFI:T:WPA;S:NetworkName;P:Password;;',
      type: 'wifi',
      scans: 156,
      uniqueScans: 89,
      created: '2026-01-05',
      lastScanned: '2026-01-17'
    },
    {
      id: 4,
      name: 'Contact Card',
      url: 'BEGIN:VCARD\nFN:John Doe\nTEL:+1234567890\nEND:VCARD',
      type: 'contact',
      scans: 234,
      uniqueScans: 145,
      created: '2025-11-20',
      lastScanned: '2026-01-16'
    }
  ];

  useEffect(() => {
    fetchQRCodes();
  }, []);

  const fetchQRCodes = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/qrcode/list`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setQRCodes(response.data.qrcodes || mockQRCodes);
    } catch (error) {
      console.error('Error fetching QR codes:', error);
      setQRCodes(mockQRCodes);
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

  const handleCreateQRCode = async (e) => {
    e.preventDefault();

    if (!formData.name || !formData.url) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const token = localStorage.getItem('authToken');
      await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/v1/qrcode/create`,
        {
          name: formData.name,
          url: formData.url,
          type: formData.type
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newQRCode = {
        id: qrCodes.length + 1,
        name: formData.name,
        url: formData.url,
        type: formData.type,
        scans: 0,
        uniqueScans: 0,
        created: new Date().toISOString().split('T')[0],
        lastScanned: null
      };

      setQRCodes(prev => [newQRCode, ...prev]);
      setFormData({ name: '', url: '', type: 'link' });
      setShowCreateForm(false);
      toast.success('QR Code created successfully!');
      fetchQRCodes();
    } catch (error) {
      console.error('Error creating QR code:', error);
      toast.error('Failed to create QR code');
    }
  };

  const copyURL = (url) => {
    navigator.clipboard.writeText(url);
    toast.success('URL copied!');
  };

  if (loading) {
    return <Container><Title><QrCode /> Loading QR Codes...</Title></Container>;
  }

  const totalScans = qrCodes.reduce((sum, q) => sum + q.scans, 0);
  const totalUnique = qrCodes.reduce((sum, q) => sum + q.uniqueScans, 0);

  return (
    <Container>
      <Header>
        <Title>
          <QrCode /> QR Code Management
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          <Plus size={20} /> Generate QR
        </Button>
      </Header>

      {showCreateForm && (
        <FormContainer>
          <h2>Generate New QR Code</h2>
          <form onSubmit={handleCreateQRCode}>
            <FormGroup>
              <Label>QR Code Name *</Label>
              <Input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="e.g., Product Page QR"
                required
              />
            </FormGroup>

            <FormGroup>
              <Label>Type</Label>
              <Select
                name="type"
                value={formData.type}
                onChange={handleInputChange}
              >
                <option value="link">Website Link</option>
                <option value="wifi">WiFi Network</option>
                <option value="contact">Contact Card</option>
                <option value="email">Email</option>
                <option value="phone">Phone Number</option>
                <option value="sms">SMS</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Content/URL *</Label>
              <Input
                type="text"
                name="url"
                value={formData.url}
                onChange={handleInputChange}
                placeholder={
                  formData.type === 'link' 
                    ? 'https://example.com'
                    : 'Enter content based on selected type'
                }
                required
              />
            </FormGroup>

            <SubmitButton type="submit">Generate QR Code</SubmitButton>
          </form>
        </FormContainer>
      )}

      <GridContainer>
        {qrCodes.map(qr => (
          <Card key={qr.id}>
            <CardTitle>
              <QrCode size={20} /> {qr.name}
            </CardTitle>

            <QRCodeBox>□■□</QRCodeBox>

            <StatsGrid>
              <StatBox color="#DBEAFE">
                <div>Total Scans</div>
                <div>{qr.scans.toLocaleString()}</div>
              </StatBox>
              <StatBox color="#DBEAFE">
                <div>Unique Scans</div>
                <div>{qr.uniqueScans.toLocaleString()}</div>
              </StatBox>
            </StatsGrid>

            <div style={{ marginTop: '15px', padding: '10px', background: '#F0F9FF', borderRadius: '6px', fontSize: '0.85rem', color: '#1E40AF' }}>
              <strong>Type:</strong> {qr.type.charAt(0).toUpperCase() + qr.type.slice(1)}
            </div>

            <URLBox>{qr.url}</URLBox>

            <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '10px' }}>
              <div><strong>Created:</strong> {qr.created}</div>
              {qr.lastScanned && <div><strong>Last Scanned:</strong> {qr.lastScanned}</div>}
            </div>

            <ButtonGroup>
              <SmallButton onClick={() => copyURL(qr.url)}>
                <Copy size={16} /> Copy
              </SmallButton>
              <SmallButton>
                <Download size={16} /> Download
              </SmallButton>
              <SmallButton>
                <BarChart3 size={16} /> Stats
              </SmallButton>
            </ButtonGroup>
          </Card>
        ))}
      </GridContainer>

      <Card style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%)' }}>
        <h3>QR Code Statistics</h3>
        <StatsGrid>
          <StatBox color="#DBEAFE">
            <div>Total QR Codes</div>
            <div>{qrCodes.length}</div>
          </StatBox>
          <StatBox color="#DBEAFE">
            <div>Total Scans</div>
            <div>{totalScans.toLocaleString()}</div>
          </StatBox>
          <StatBox color="#BFDBFE">
            <div>Unique Scans</div>
            <div>{totalUnique.toLocaleString()}</div>
          </StatBox>
          <StatBox color="#BFDBFE">
            <div>Avg Scans/QR</div>
            <div>{(totalScans / qrCodes.length).toFixed(0)}</div>
          </StatBox>
        </StatsGrid>
      </Card>
    </Container>
  );
};

export default QRCodeTab;
