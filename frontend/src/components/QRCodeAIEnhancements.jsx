import React, { useState, useEffect } from "react";
import styled from "styled-components";
import {
  Brain,
  TrendingUp,
  Zap,
  Target,
  BarChart3,
  Lightbulb,
  Loader2,
  CheckCircle,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

// ============ STYLED COMPONENTS ============

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Card = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: #333;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 12px;

  svg {
    width: 24px;
    height: 24px;
    color: #667eea;
  }
`;

const InsightGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
`;

const InsightBox = styled.div`
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InsightLabel = styled.span`
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const InsightValue = styled.span`
  font-size: 16px;
  font-weight: 700;
  color: #667eea;
`;

const InsightDescription = styled.p`
  font-size: 13px;
  color: #666;
  margin: 0;
  line-height: 1.4;
`;

const PredictionContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const PredictionCard = styled.div`
  background: linear-gradient(135deg, ${(props) => props.color || "#667eea"} 0%, ${(props) => props.darkColor || "#764ba2"} 100%);
  border-radius: 12px;
  padding: 20px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const PredictionLabel = styled.span`
  font-size: 12px;
  opacity: 0.9;
  text-transform: uppercase;
`;

const PredictionValue = styled.span`
  font-size: 28px;
  font-weight: 700;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
  gap: 12px;
  color: #667eea;
`;

const RecommendationList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const RecommendationItem = styled.li`
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(102, 126, 234, 0.05);
  border-left: 3px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  color: #666;

  svg {
    width: 20px;
    height: 20px;
    color: #667eea;
    flex-shrink: 0;
    margin-top: 2px;
  }
`;

const ConfidenceScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #999;

  .bar {
    height: 4px;
    background: #e0e0e0;
    border-radius: 2px;
    overflow: hidden;
    width: 60px;

    .fill {
      height: 100%;
      background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
      width: ${(props) => props.score * 100}%;
      transition: width 0.3s ease;
    }
  }
`;

// ============ COMPONENT ============

export default function QRCodeAIEnhancements({ qrId, userId }) {
  const [insights, setInsights] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("insights");

  const loadSmartInsights = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE_URL}/api/qrcode/ai/smart-insights/${qrId}`,
        { params: { user_id: userId } }
      );
      setInsights(response.data);
    } catch (error) {
      console.error("Failed to load insights:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadPredictions = async () => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE_URL}/api/qrcode/ai/predict-engagement`,
        {},
        { params: { qr_id: qrId, user_id: userId } }
      );
      setPredictions(response.data.prediction);
    } catch (error) {
      console.error("Failed to load predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE_URL}/api/qrcode/ai/campaign-recommendations`,
        {
          industry: "general",
          goal: "increase engagement",
          audience: "general",
          budget: "unlimited",
          timeline: "1 month",
        },
        { params: { user_id: userId } }
      );
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error("Failed to load recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === "insights" && !insights) loadSmartInsights();
    if (activeTab === "predictions" && !predictions) loadPredictions();
    if (activeTab === "recommendations" && !recommendations) loadRecommendations();
  }, [activeTab]);

  const renderInsights = () => (
    <Container>
      <Card>
        <CardTitle>
          <Brain /> AI Pattern Analysis
        </CardTitle>
        {loading ? (
          <LoadingContainer>
            <Loader2 style={{ animation: "spin 2s linear infinite" }} />
            Analyzing patterns...
          </LoadingContainer>
        ) : insights ? (
          <div>
            <InsightGrid>
              <InsightBox>
                <InsightLabel>Total Scans</InsightLabel>
                <InsightValue>{insights.metrics?.total_scans || 0}</InsightValue>
              </InsightBox>
              <InsightBox>
                <InsightLabel>Unique Users</InsightLabel>
                <InsightValue>{insights.metrics?.unique_scans || 0}</InsightValue>
              </InsightBox>
              <InsightBox>
                <InsightLabel>Conversion Rate</InsightLabel>
                <InsightValue>{insights.metrics?.conversion_rate?.toFixed(1) || 0}%</InsightValue>
              </InsightBox>
            </InsightGrid>

            {insights.analysis && (
              <div style={{ marginTop: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Key Insights</h4>
                <InsightDescription>{insights.analysis.insights}</InsightDescription>
                <div style={{ marginTop: "12px" }}>
                  <strong>Device Recommendations:</strong>
                  <InsightDescription>{insights.analysis.device_rec}</InsightDescription>
                </div>
                <div style={{ marginTop: "12px" }}>
                  <strong>Geographic Insights:</strong>
                  <InsightDescription>{insights.analysis.geo_insights}</InsightDescription>
                </div>
              </div>
            )}

            {insights.patterns?.analysis && (
              <div style={{ marginTop: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Scan Pattern Detection</h4>
                <InsightDescription>{insights.patterns.analysis}</InsightDescription>
              </div>
            )}

            <Button onClick={loadSmartInsights} style={{ marginTop: "20px" }}>
              <RefreshCw /> Refresh Analysis
            </Button>
          </div>
        ) : (
          <Button onClick={loadSmartInsights}>
            <Brain /> Run AI Analysis
          </Button>
        )}
      </Card>
    </Container>
  );

  const renderPredictions = () => (
    <Container>
      <Card>
        <CardTitle>
          <TrendingUp /> Engagement Predictions
        </CardTitle>
        {loading ? (
          <LoadingContainer>
            <Loader2 style={{ animation: "spin 2s linear infinite" }} />
            Running predictions...
          </LoadingContainer>
        ) : predictions ? (
          <div>
            <PredictionContainer>
              <PredictionCard color="#667eea" darkColor="#764ba2">
                <PredictionLabel>Trend</PredictionLabel>
                <PredictionValue style={{ textTransform: "capitalize" }}>
                  {predictions.prediction}
                </PredictionValue>
              </PredictionCard>
              <PredictionCard color="#06b6d4" darkColor="#0891b2">
                <PredictionLabel>Scans/Day</PredictionLabel>
                <PredictionValue>{predictions.scans_per_day || 0}</PredictionValue>
              </PredictionCard>
              <PredictionCard color="#8b5cf6" darkColor="#7c3aed">
                <PredictionLabel>Confidence</PredictionLabel>
                <PredictionValue>{(predictions.confidence * 100)?.toFixed(0)}%</PredictionValue>
              </PredictionCard>
            </PredictionContainer>

            <ConfidenceScore score={predictions.confidence} style={{ marginTop: "20px" }}>
              <span>Model Confidence</span>
              <div className="bar">
                <div className="fill"></div>
              </div>
            </ConfidenceScore>

            <Button onClick={loadPredictions} style={{ marginTop: "20px" }}>
              <RefreshCw /> Update Predictions
            </Button>
          </div>
        ) : (
          <Button onClick={loadPredictions}>
            <TrendingUp /> Run Predictions
          </Button>
        )}
      </Card>
    </Container>
  );

  const renderRecommendations = () => (
    <Container>
      <Card>
        <CardTitle>
          <Lightbulb /> AI Recommendations
        </CardTitle>
        {loading ? (
          <LoadingContainer>
            <Loader2 style={{ animation: "spin 2s linear infinite" }} />
            Generating recommendations...
          </LoadingContainer>
        ) : recommendations ? (
          <div>
            {recommendations.qr_type && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Recommended QR Types</h4>
                <RecommendationList>
                  {(Array.isArray(recommendations.qr_type) ? recommendations.qr_type : [recommendations.qr_type]).map((type, idx) => (
                    <RecommendationItem key={idx}>
                      <CheckCircle />
                      <span>{type}</span>
                    </RecommendationItem>
                  ))}
                </RecommendationList>
              </div>
            )}

            {recommendations.design_tips && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Design Tips</h4>
                <InsightDescription>{recommendations.design_tips}</InsightDescription>
              </div>
            )}

            {recommendations.channels && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Distribution Channels</h4>
                <RecommendationList>
                  {(Array.isArray(recommendations.channels) ? recommendations.channels : [recommendations.channels]).map((channel, idx) => (
                    <RecommendationItem key={idx}>
                      <Target />
                      <span style={{ textTransform: "capitalize" }}>{channel}</span>
                    </RecommendationItem>
                  ))}
                </RecommendationList>
              </div>
            )}

            {recommendations.expected_roi && (
              <div style={{ marginBottom: "20px" }}>
                <h4 style={{ color: "#333", marginTop: 0 }}>Expected ROI</h4>
                <InsightDescription>{recommendations.expected_roi}</InsightDescription>
              </div>
            )}

            <Button onClick={loadRecommendations} style={{ marginTop: "20px" }}>
              <RefreshCw /> Refresh Recommendations
            </Button>
          </div>
        ) : (
          <Button onClick={loadRecommendations}>
            <Lightbulb /> Generate Recommendations
          </Button>
        )}
      </Card>
    </Container>
  );

  return (
    <Container>
      <Card>
        <div style={{ display: "flex", gap: "12px", marginBottom: "20px", flexWrap: "wrap" }}>
          <Button
            primary={activeTab === "insights"}
            onClick={() => setActiveTab("insights")}
            style={{
              background: activeTab === "insights" ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "rgba(102, 126, 234, 0.1)",
              color: activeTab === "insights" ? "white" : "#667eea",
            }}
          >
            <Brain /> Insights
          </Button>
          <Button
            primary={activeTab === "predictions"}
            onClick={() => setActiveTab("predictions")}
            style={{
              background: activeTab === "predictions" ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "rgba(102, 126, 234, 0.1)",
              color: activeTab === "predictions" ? "white" : "#667eea",
            }}
          >
            <TrendingUp /> Predictions
          </Button>
          <Button
            primary={activeTab === "recommendations"}
            onClick={() => setActiveTab("recommendations")}
            style={{
              background: activeTab === "recommendations" ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "rgba(102, 126, 234, 0.1)",
              color: activeTab === "recommendations" ? "white" : "#667eea",
            }}
          >
            <Lightbulb /> Recommendations
          </Button>
        </div>

        {activeTab === "insights" && renderInsights()}
        {activeTab === "predictions" && renderPredictions()}
        {activeTab === "recommendations" && renderRecommendations()}
      </Card>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Container>
  );
}
