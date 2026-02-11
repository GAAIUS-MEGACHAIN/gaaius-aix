import React, { useState, useEffect, useCallback, useRef } from "react";
import styled from "styled-components";
import QRCodeAIEnhancements from "./QRCodeAIEnhancements";
import {
  QrCode,
  Plus,
  Download,
  Copy,
  Eye,
  Trash2,
  Settings,
  BarChart3,
  Share2,
  Edit3,
  Smartphone,
  Link,
  User,
  Send,
  Wifi,
  Mail,
  Calendar,
  Package,
  Tag,
  Zap,
  TrendingUp,
  MapPin,
  Globe,
  Clock,
  Check,
  X,
  Upload,
  List,
} from "lucide-react";
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

// ============ STYLED COMPONENTS ============

const Container = styled.div`
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  overflow: hidden;
`;

const Sidebar = styled.div`
  width: 280px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  padding: 30px 20px;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const NavMenu = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const NavItem = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  background: ${(props) => (props.active ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "transparent")};
  color: ${(props) => (props.active ? "white" : "#333")};
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    background: ${(props) => (props.active ? "" : "rgba(102, 126, 234, 0.1)")};
    transform: translateX(4px);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const TopBar = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 20px 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const PageTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const UserName = styled.span`
  font-size: 14px;
  color: #666;
  font-weight: 500;
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);

  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 4px;

    &:hover {
      background: rgba(102, 126, 234, 0.5);
    }
  }
`;

const TabContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  overflow-x: auto;
  padding-bottom: 0;

  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
  }
`;

const Tab = styled.button`
  padding: 12px 20px;
  background: transparent;
  color: ${(props) => (props.active ? "#667eea" : "#999")};
  border: none;
  border-bottom: 3px solid ${(props) => (props.active ? "#667eea" : "transparent")};
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;

  &:hover {
    color: #667eea;
  }
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
`;

const SectionTitle = styled.h2`
  font-size: 20px;
  font-weight: 600;
  color: white;
  margin: 0;
`;

const ActionBar = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: ${(props) => (props.small ? "8px 12px" : "12px 20px")};
  background: ${(props) => {
    if (props.primary) return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
    if (props.danger) return "rgba(255, 74, 74, 0.2)";
    return "rgba(255, 255, 255, 0.1)";
  }};
  color: ${(props) => (props.danger ? "#ff4a4a" : "white")};
  border: ${(props) => (props.outlined ? "1px solid rgba(255, 255, 255, 0.3)" : "none")};
  border-radius: 8px;
  cursor: pointer;
  font-size: ${(props) => (props.small ? "12px" : "14px")};
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    background: ${(props) => {
      if (props.primary) return "linear-gradient(135deg, #5a6fd4 0%, #6a3f94 100%)";
      if (props.danger) return "rgba(255, 74, 74, 0.3)";
      return "rgba(255, 255, 255, 0.2)";
    }};
    transform: translateY(-2px);
  }

  svg {
    width: ${(props) => (props.small ? "16px" : "20px")};
    height: ${(props) => (props.small ? "16px" : "20px")};
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  cursor: ${(props) => (props.clickable ? "pointer" : "default")};

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    border-color: rgba(102, 126, 234, 0.5);
  }
`;

const QRCardContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const QRImage = styled.img`
  width: 100%;
  height: 200px;
  object-fit: contain;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
`;

const CardTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const CardDescription = styled.p`
  font-size: 13px;
  color: #666;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const CardCode = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(102, 126, 234, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #667eea;
  font-family: "Courier New", monospace;
`;

const CardActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const Modal = styled.div`
  display: ${(props) => (props.open ? "flex" : "none")};
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;

  @keyframes slideUp {
    from {
      transform: translateY(30px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
`;

const ModalTitle = styled.h2`
  font-size: 22px;
  font-weight: 700;
  color: #333;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const CloseButton = styled.button`
  background: rgba(0, 0, 0, 0.05);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 18px;
`;

const Label = styled.label`
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  font-size: 14px;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  resize: vertical;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

const QRPreview = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  margin-bottom: 20px;
`;

const QRPreviewImage = styled.img`
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
`;

const AnalyticsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
`;

const AnalyticsCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const AnalyticsLabel = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
`;

const AnalyticsValue = styled.span`
  font-size: 28px;
  font-weight: 700;
  color: #667eea;
`;

const ScanEventsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ScanEventItem = styled.div`
  background: rgba(102, 126, 234, 0.05);
  border-left: 3px solid #667eea;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
`;

const BadgeContainer = styled.div`
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
`;

const Badge = styled.span`
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: #667eea;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.6);
`;

const EmptyStateIcon = styled.div`
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
`;

const EmptyStateText = styled.p`
  font-size: 16px;
  margin: 0;
  text-align: center;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
`;

const TableHead = styled.thead`
  background: rgba(102, 126, 234, 0.1);
`;

const TableRow = styled.tr`
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);

  &:hover {
    background: rgba(102, 126, 234, 0.05);
  }
`;

const TableCell = styled.td`
  padding: 14px;
  font-size: 13px;
  color: #333;

  ${(props) => props.header && `
    font-weight: 600;
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  `}
`;

// ============ MAIN COMPONENT ============

export default function QRCodeDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [qrCodes, setQrCodes] = useState([]);
  const [selectedQR, setSelectedQR] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    qr_type: "url",
    title: "",
    description: "",
    campaign_name: "",
    tags: "",
    content: { url: "" },
  });
  const [qrPreview, setQrPreview] = useState(null);
  const userId = "user123"; // Replace with actual user

  // Load QR codes on mount
  useEffect(() => {
    loadQRCodes();
  }, []);

  const loadQRCodes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/qrcode/list`, {
        params: { user_id: userId },
      });
      setQrCodes(response.data.qr_codes || []);
    } catch (error) {
      console.error("Failed to load QR codes:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async () => {
    try {
      setLoading(true);
      const payload = {
        qr_type: formData.qr_type,
        title: formData.title,
        description: formData.description,
        campaign_name: formData.campaign_name,
        tags: formData.tags.split(",").filter((t) => t.trim()),
        content: formData.content,
        design: {
          color_dark: "#000000",
          color_light: "#FFFFFF",
          pattern_type: "square",
        },
        metadata: {
          type: formData.qr_type,
          title: formData.title,
          description: formData.description,
        },
      };

      const response = await axios.post(`${API_BASE_URL}/api/qrcode/generate`, payload, {
        params: { user_id: userId },
      });

      setQrPreview(response.data.qr_image_base64);
      setQrCodes([...qrCodes, response.data]);
      setFormData({
        qr_type: "url",
        title: "",
        description: "",
        campaign_name: "",
        tags: "",
        content: { url: "" },
      });
      setQrPreview(null);
      setShowCreateModal(false);
    } catch (error) {
      console.error("Failed to generate QR code:", error);
      alert("Failed to generate QR code");
    } finally {
      setLoading(false);
    }
  };

  const downloadQRCode = (base64, filename) => {
    const link = document.createElement("a");
    link.href = `data:image/png;base64,${base64}`;
    link.download = filename || "qrcode.png";
    link.click();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  const deleteQRCode = async (qr_id) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      await axios.delete(`${API_BASE_URL}/api/qrcode/${qr_id}`, {
        params: { user_id: userId },
      });
      setQrCodes(qrCodes.filter((q) => q._id !== qr_id));
    } catch (error) {
      console.error("Failed to delete:", error);
    }
  };

  const viewAnalytics = async (qr) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/qrcode/${qr._id}/analytics`, {
        params: { user_id: userId },
      });
      setSelectedQR(qr);
      setAnalytics(response.data);
      setShowAnalyticsModal(true);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith("content_")) {
      const contentKey = name.replace("content_", "");
      setFormData({
        ...formData,
        content: { ...formData.content, [contentKey]: value },
      });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  // ============ RENDER TABS ============

  const renderDashboard = () => (
    <div>
      <SectionHeader>
        <SectionTitle>Dashboard</SectionTitle>
        <Button primary onClick={() => setShowCreateModal(true)}>
          <Plus size={20} /> Create QR Code
        </Button>
      </SectionHeader>

      <AnalyticsGrid>
        <AnalyticsCard>
          <AnalyticsLabel>Total QR Codes</AnalyticsLabel>
          <AnalyticsValue>{qrCodes.length}</AnalyticsValue>
        </AnalyticsCard>
        <AnalyticsCard>
          <AnalyticsLabel>Active Codes</AnalyticsLabel>
          <AnalyticsValue>{qrCodes.filter((q) => q.is_active).length}</AnalyticsValue>
        </AnalyticsCard>
        <AnalyticsCard>
          <AnalyticsLabel>Total Scans</AnalyticsLabel>
          <AnalyticsValue>{qrCodes.reduce((sum, q) => sum + (q.access_count || 0), 0)}</AnalyticsValue>
        </AnalyticsCard>
      </AnalyticsGrid>

      {qrCodes.length === 0 ? (
        <EmptyState>
          <EmptyStateIcon>📱</EmptyStateIcon>
          <EmptyStateText>No QR codes yet. Create your first one!</EmptyStateText>
        </EmptyState>
      ) : (
        <Grid>
          {qrCodes.slice(0, 6).map((qr) => (
            <Card key={qr._id}>
              <QRCardContent>
                <QRImage src={`data:image/png;base64,${qr.qr_image_base64}`} alt={qr.title} />
                <CardTitle>{qr.title || "Untitled"}</CardTitle>
                <CardDescription>{qr.description}</CardDescription>
                <CardCode>{qr.short_code}</CardCode>
                <BadgeContainer>
                  <Badge>{qr.qr_type}</Badge>
                  <Badge>{qr.access_count} scans</Badge>
                </BadgeContainer>
                <CardActions>
                  <Button
                    small
                    primary
                    onClick={() => {
                      setSelectedQR(qr);
                      setShowDetailsModal(true);
                    }}
                  >
                    <Eye size={16} />
                  </Button>
                  <Button small onClick={() => downloadQRCode(qr.qr_image_base64, qr.title)}>
                    <Download size={16} />
                  </Button>
                  <Button small onClick={() => copyToClipboard(`qr/${qr.short_code}`)}>
                    <Copy size={16} />
                  </Button>
                  <Button small onClick={() => viewAnalytics(qr)}>
                    <BarChart3 size={16} />
                  </Button>
                  <Button small danger onClick={() => deleteQRCode(qr._id)}>
                    <Trash2 size={16} />
                  </Button>
                </CardActions>
              </QRCardContent>
            </Card>
          ))}
        </Grid>
      )}
    </div>
  );

  const renderCreateQR = () => (
    <div>
      <SectionHeader>
        <SectionTitle>Create New QR Code</SectionTitle>
      </SectionHeader>

      <Card style={{ maxWidth: "800px", margin: "0 auto", marginBottom: "20px" }}>
        <FormGroup>
          <Label>QR Code Type</Label>
          <Select name="qr_type" value={formData.qr_type} onChange={handleFormChange}>
            <option value="url">URL Link</option>
            <option value="vcard">Contact (vCard)</option>
            <option value="sms">SMS</option>
            <option value="email">Email</option>
            <option value="wifi">WiFi</option>
            <option value="event">Event</option>
            <option value="product">Product</option>
            <option value="coupon">Coupon</option>
          </Select>
        </FormGroup>

        <FormRow>
          <FormGroup>
            <Label>Title</Label>
            <Input
              type="text"
              name="title"
              placeholder="QR Code title"
              value={formData.title}
              onChange={handleFormChange}
            />
          </FormGroup>
          <FormGroup>
            <Label>Campaign Name</Label>
            <Input
              type="text"
              name="campaign_name"
              placeholder="Campaign name"
              value={formData.campaign_name}
              onChange={handleFormChange}
            />
          </FormGroup>
        </FormRow>

        <FormGroup>
          <Label>Description</Label>
          <TextArea
            name="description"
            placeholder="QR code description"
            value={formData.description}
            onChange={handleFormChange}
            rows="3"
          />
        </FormGroup>

        <FormGroup>
          <Label>Tags</Label>
          <Input
            type="text"
            name="tags"
            placeholder="tag1, tag2, tag3"
            value={formData.tags}
            onChange={handleFormChange}
          />
        </FormGroup>

        {formData.qr_type === "url" && (
          <FormGroup>
            <Label>URL</Label>
            <Input
              type="url"
              name="content_url"
              placeholder="https://example.com"
              value={formData.content.url || ""}
              onChange={handleFormChange}
            />
          </FormGroup>
        )}

        {formData.qr_type === "sms" && (
          <FormRow>
            <FormGroup>
              <Label>Phone Number</Label>
              <Input
                type="tel"
                name="content_phone"
                placeholder="+1234567890"
                value={formData.content.phone || ""}
                onChange={handleFormChange}
              />
            </FormGroup>
            <FormGroup>
              <Label>Message</Label>
              <Input
                type="text"
                name="content_message"
                placeholder="Message"
                value={formData.content.message || ""}
                onChange={handleFormChange}
              />
            </FormGroup>
          </FormRow>
        )}

        {formData.qr_type === "email" && (
          <FormRow>
            <FormGroup>
              <Label>Email</Label>
              <Input
                type="email"
                name="content_email"
                placeholder="contact@example.com"
                value={formData.content.email || ""}
                onChange={handleFormChange}
              />
            </FormGroup>
            <FormGroup>
              <Label>Subject</Label>
              <Input
                type="text"
                name="content_subject"
                placeholder="Email subject"
                value={formData.content.subject || ""}
                onChange={handleFormChange}
              />
            </FormGroup>
          </FormRow>
        )}

        <Button primary style={{ width: "100%" }} onClick={generateQRCode} disabled={loading}>
          {loading ? "Generating..." : "Generate QR Code"}
        </Button>
      </Card>
    </div>
  );

  const renderAllQRCodes = () => (
    <div>
      <SectionHeader>
        <SectionTitle>All QR Codes</SectionTitle>
        <Button primary onClick={() => setShowCreateModal(true)}>
          <Plus size={20} /> Create
        </Button>
      </SectionHeader>

      {qrCodes.length === 0 ? (
        <EmptyState>
          <EmptyStateIcon>📊</EmptyStateIcon>
          <EmptyStateText>No QR codes created yet</EmptyStateText>
        </EmptyState>
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell header>Title</TableCell>
              <TableCell header>Type</TableCell>
              <TableCell header>Short Code</TableCell>
              <TableCell header>Scans</TableCell>
              <TableCell header>Status</TableCell>
              <TableCell header>Actions</TableCell>
            </TableRow>
          </TableHead>
          <tbody>
            {qrCodes.map((qr) => (
              <TableRow key={qr._id}>
                <TableCell>{qr.title || "Untitled"}</TableCell>
                <TableCell>{qr.qr_type}</TableCell>
                <TableCell>{qr.short_code}</TableCell>
                <TableCell>{qr.access_count}</TableCell>
                <TableCell>{qr.is_active ? "Active" : "Inactive"}</TableCell>
                <TableCell>
                  <ActionBar>
                    <Button small primary onClick={() => viewAnalytics(qr)}>
                      <BarChart3 size={16} />
                    </Button>
                    <Button small onClick={() => downloadQRCode(qr.qr_image_base64, qr.title)}>
                      <Download size={16} />
                    </Button>
                    <Button small danger onClick={() => deleteQRCode(qr._id)}>
                      <Trash2 size={16} />
                    </Button>
                  </ActionBar>
                </TableCell>
              </TableRow>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );

  // ============ MODALS ============

  const renderCreateModal = () => (
    <Modal open={showCreateModal}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>
            <QrCode size={24} /> Create QR Code
          </ModalTitle>
          <CloseButton onClick={() => setShowCreateModal(false)}>
            <X size={20} />
          </CloseButton>
        </ModalHeader>

        <FormGroup>
          <Label>QR Code Type</Label>
          <Select name="qr_type" value={formData.qr_type} onChange={handleFormChange}>
            <option value="url">URL Link</option>
            <option value="vcard">Contact (vCard)</option>
            <option value="sms">SMS</option>
            <option value="email">Email</option>
            <option value="wifi">WiFi</option>
            <option value="event">Event</option>
            <option value="product">Product</option>
            <option value="coupon">Coupon</option>
          </Select>
        </FormGroup>

        <FormRow>
          <FormGroup>
            <Label>Title</Label>
            <Input
              type="text"
              name="title"
              placeholder="QR Code title"
              value={formData.title}
              onChange={handleFormChange}
            />
          </FormGroup>
          <FormGroup>
            <Label>Campaign</Label>
            <Input
              type="text"
              name="campaign_name"
              placeholder="Campaign name"
              value={formData.campaign_name}
              onChange={handleFormChange}
            />
          </FormGroup>
        </FormRow>

        <FormGroup>
          <Label>Description</Label>
          <TextArea
            name="description"
            placeholder="QR code description"
            value={formData.description}
            onChange={handleFormChange}
            rows="2"
          />
        </FormGroup>

        {formData.qr_type === "url" && (
          <FormGroup>
            <Label>URL</Label>
            <Input
              type="url"
              name="content_url"
              placeholder="https://example.com"
              value={formData.content.url || ""}
              onChange={handleFormChange}
            />
          </FormGroup>
        )}

        {qrPreview && (
          <QRPreview>
            <QRPreviewImage src={`data:image/png;base64,${qrPreview}`} alt="QR Preview" />
          </QRPreview>
        )}

        <Button primary style={{ width: "100%" }} onClick={generateQRCode} disabled={loading}>
          {loading ? "Generating..." : "Generate QR Code"}
        </Button>
      </ModalContent>
    </Modal>
  );

  const renderDetailsModal = () => (
    <Modal open={showDetailsModal && !!selectedQR}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>QR Code Details</ModalTitle>
          <CloseButton onClick={() => setShowDetailsModal(false)}>
            <X size={20} />
          </CloseButton>
        </ModalHeader>

        {selectedQR && (
          <div>
            <QRPreview>
              <QRPreviewImage src={`data:image/png;base64,${selectedQR.qr_image_base64}`} alt="QR" />
            </QRPreview>

            <FormGroup>
              <Label>Title</Label>
              <Input type="text" value={selectedQR.title || ""} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Short Code</Label>
              <Input type="text" value={selectedQR.short_code || ""} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Type</Label>
              <Input type="text" value={selectedQR.qr_type} disabled />
            </FormGroup>

            <FormGroup>
              <Label>Description</Label>
              <TextArea value={selectedQR.description || ""} disabled rows="3" />
            </FormGroup>

            <ActionBar>
              <Button
                primary
                onClick={() => downloadQRCode(selectedQR.qr_image_base64, selectedQR.title)}
              >
                <Download size={20} /> Download
              </Button>
              <Button onClick={() => copyToClipboard(selectedQR.short_code)}>
                <Copy size={20} /> Copy Code
              </Button>
              <Button onClick={() => viewAnalytics(selectedQR)}>
                <BarChart3 size={20} /> Analytics
              </Button>
            </ActionBar>
          </div>
        )}
      </ModalContent>
    </Modal>
  );

  const renderAnalyticsModal = () => (
    <Modal open={showAnalyticsModal && !!analytics}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>QR Code Analytics</ModalTitle>
          <CloseButton onClick={() => setShowAnalyticsModal(false)}>
            <X size={20} />
          </CloseButton>
        </ModalHeader>

        {analytics && (
          <div>
            <AnalyticsGrid>
              <AnalyticsCard>
                <AnalyticsLabel>Total Scans</AnalyticsLabel>
                <AnalyticsValue>{analytics.total_scans || 0}</AnalyticsValue>
              </AnalyticsCard>
              <AnalyticsCard>
                <AnalyticsLabel>Unique Scans</AnalyticsLabel>
                <AnalyticsValue>{analytics.unique_scans || 0}</AnalyticsValue>
              </AnalyticsCard>
            </AnalyticsGrid>

            {analytics.scan_events && analytics.scan_events.length > 0 && (
              <FormGroup>
                <Label>Recent Scans</Label>
                <ScanEventsList>
                  {analytics.scan_events.slice(-5).map((event, idx) => (
                    <ScanEventItem key={idx}>
                      📱 {event.device_type} - {new Date(event.timestamp).toLocaleString()}
                    </ScanEventItem>
                  ))}
                </ScanEventsList>
              </FormGroup>
            )}
          </div>
        )}
      </ModalContent>
    </Modal>
  );

  // ============ MAIN RENDER ============

  return (
    <Container>
      <Sidebar>
        <Logo>
          <QrCode size={28} /> QRCode
        </Logo>
        <NavMenu>
          <NavItem active={activeTab === "dashboard"} onClick={() => setActiveTab("dashboard")}>
            <Globe size={20} />
            Dashboard
          </NavItem>
          <NavItem active={activeTab === "create"} onClick={() => setActiveTab("create")}>
            <Plus size={20} />
            Create
          </NavItem>
          <NavItem active={activeTab === "list"} onClick={() => setActiveTab("list")}>
            <List size={20} />
            All Codes
          </NavItem>
          <NavItem active={activeTab === "analytics"} onClick={() => setActiveTab("analytics")}>
            <TrendingUp size={20} />
            Analytics
          </NavItem>
          <NavItem active={activeTab === "ai"} onClick={() => setActiveTab("ai")}>
            <Zap size={20} />
            AI Insights
          </NavItem>
        </NavMenu>
      </Sidebar>

      <MainContent>
        <TopBar>
          <PageTitle>
            <QrCode size={28} /> QR Code Generator
          </PageTitle>
          <UserInfo>
            <UserName>Enterprise QRCode Studio</UserName>
          </UserInfo>
        </TopBar>

        <Content>
          {activeTab === "dashboard" && renderDashboard()}
          {activeTab === "create" && renderCreateQR()}
          {activeTab === "list" && renderAllQRCodes()}
          {activeTab === "analytics" && (
            <div>
              <SectionTitle>QR Code Analytics</SectionTitle>
              <p style={{ color: "white", marginTop: "20px" }}>
                Click on any QR code to view detailed analytics
              </p>
            </div>
          )}
          {activeTab === "ai" && (
            <QRCodeAIEnhancements />
          )}
        </Content>
      </MainContent>

      {renderCreateModal()}
      {renderDetailsModal()}
      {renderAnalyticsModal()}
    </Container>
  );
}
