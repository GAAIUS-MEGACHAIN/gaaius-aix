import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Gem, Plus, Zap, TrendingUp, Copy } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
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

const NFTTab = () => {
  const [nfts, setNfts] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const token = localStorage.getItem('gaaius_token');

  const mockNFTs = [
    {
      nft_id: '1',
      name: 'Digital Art #001',
      blockchain: 'Ethereum',
      price: '5.2 ETH',
      royalty: '10%',
      owners: 42
    },
    {
      nft_id: '2',
      name: 'Collectible #042',
      blockchain: 'Polygon',
      price: '0.8 POL',
      royalty: '7.5%',
      owners: 128
    },
    {
      nft_id: '3',
      name: 'Rare Asset #007',
      blockchain: 'Solana',
      price: '12.5 SOL',
      royalty: '5%',
      owners: 76
    }
  ];

  return (
    <Container>
      <Header>
        <Title>
          <Gem size={32} />
          NFT Marketplace
        </Title>
        <Button style={{ width: 'auto' }}>
          <Plus size={16} style={{ display: 'inline', marginRight: '5px' }} />
          Mint NFT
        </Button>
      </Header>

      <GridContainer>
        {mockNFTs.map((nft) => (
          <Card key={nft.nft_id}>
            <h3 style={{ margin: '0 0 10px 0' }}>{nft.name}</h3>
            <StatRow>
              <span style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.6)' }}>
                Blockchain
              </span>
              <span style={{ fontSize: '12px', fontWeight: 'bold' }}>
                {nft.blockchain}
              </span>
            </StatRow>
            <StatRow>
              <span>Price: {nft.price}</span>
            </StatRow>
            <StatRow>
              <span style={{ fontSize: '12px' }}>
                <Zap size={14} style={{ display: 'inline', marginRight: '5px' }} />
                Royalty: {nft.royalty}
              </span>
            </StatRow>
            <StatRow>
              <span style={{ fontSize: '12px' }}>Owners: {nft.owners}</span>
            </StatRow>
            <Button style={{ marginTop: '15px' }}>View Details</Button>
            <Button style={{ marginTop: '10px' }}>
              <Copy size={14} style={{ display: 'inline', marginRight: '5px' }} />
              Share
            </Button>
          </Card>
        ))}
      </GridContainer>
    </Container>
  );
};

export default NFTTab;
