import React, { useState } from 'react';
import styled from 'styled-components';
import { ChevronDown, ChevronRight } from 'lucide-react';

const MenuContainer = styled.div`
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
`;

const MenuTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: white;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CategoryGroup = styled.div`
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const CategoryHeader = styled.button`
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
  }
`;

const ServicesList = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 10px;
  max-height: ${props => (props.isOpen ? '500px' : '0')};
  overflow: hidden;
  transition: max-height 0.3s ease;
`;

const ServiceItem = styled.button`
  background: linear-gradient(135deg, ${props => props.color || '#667eea'}22 0%, ${props => props.color || '#667eea'}11 100%);
  border: 1px solid ${props => props.color || '#667eea'}44;
  color: white;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(135deg, ${props => props.color || '#667eea'}33 0%, ${props => props.color || '#667eea'}22 100%);
    border-color: ${props => props.color || '#667eea'}66;
    transform: translateX(5px);
  }
`;

const IconWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
`;

const ServicesMenu = ({ servicesConfig, onServiceSelect }) => {
  const [expandedCategories, setExpandedCategories] = useState({
    "Content & Streaming": true,
    "Creator Tools": false,
    "Commerce": false,
    "Monetization": false,
    "Utilities": false
  });

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  return (
    <MenuContainer>
      <MenuTitle>📱 Enterprise Services</MenuTitle>
      
      {Object.entries(servicesConfig).map(([category, services]) => (
        <CategoryGroup key={category}>
          <CategoryHeader
            onClick={() => toggleCategory(category)}
          >
            <span>{category}</span>
            <span style={{ transform: expandedCategories[category] ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.3s ease' }}>
              <ChevronDown size={18} />
            </span>
          </CategoryHeader>
          
          <ServicesList isOpen={expandedCategories[category]}>
            {services.map((service) => (
              <ServiceItem
                key={service.id}
                color={service.color}
                onClick={() => onServiceSelect(service.id)}
                title={service.label}
              >
                <IconWrapper>
                  <service.icon size={16} />
                </IconWrapper>
                <span>{service.label}</span>
              </ServiceItem>
            ))}
          </ServicesList>
        </CategoryGroup>
      ))}
    </MenuContainer>
  );
};

export default ServicesMenu;
