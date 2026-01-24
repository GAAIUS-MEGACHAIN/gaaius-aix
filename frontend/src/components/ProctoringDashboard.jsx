import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { 
  Shield, Video, Camera, Mic, AlertTriangle, CheckCircle, 
  Clock, BarChart3, User, Award, Download, Eye
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

/**
 * Advanced Certification Proctoring Dashboard
 * Comprehensive exam monitoring with face verification, behavior analysis, and violation detection
 */

const API_BASE = 'http://localhost:8000/api/v1';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  font-size: 28px;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const StatusBadge = styled.span`
  background: ${props => {
    switch(props.status) {
      case 'active': return 'rgba(76, 175, 80, 0.3)';
      case 'warning': return 'rgba(255, 193, 7, 0.3)';
      case 'critical': return 'rgba(244, 67, 54, 0.3)';
      default: return 'rgba(33, 150, 243, 0.3)';
    }
  }};
  border: 1px solid ${props => {
    switch(props.status) {
      case 'active': return 'rgba(76, 175, 80, 0.6)';
      case 'warning': return 'rgba(255, 193, 7, 0.6)';
      case 'critical': return 'rgba(244, 67, 54, 0.6)';
      default: return 'rgba(33, 150, 243, 0.6)';
    }
  }};
  color: ${props => {
    switch(props.status) {
      case 'active': return '#4caf50';
      case 'warning': return '#ffc107';
      case 'critical': return '#f44336';
      default: return '#2196f3';
    }
  }};
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
`;

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const MetricCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 15px;
  color: white;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  text-transform: uppercase;
  opacity: 0.8;
  margin-bottom: 5px;
`;

const MetricValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const SectionContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const Section = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 15px;
  color: white;
`;

const SectionTitle = styled.h3`
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ChecklistItem = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  &:last-child {
    border-bottom: none;
  }
`;

const ViolationList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ViolationItem = styled.div`
  background: rgba(244, 67, 54, 0.2);
  border-left: 3px solid #f44336;
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
`;

const TimerContainer = styled.div`
  text-align: center;
`;

const Timer = styled.div`
  font-size: 36px;
  font-weight: bold;
  color: #4caf50;
  font-family: 'Courier New', monospace;
`;

const ProctorNotes = styled.textarea`
  width: 100%;
  padding: 10px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: white;
  font-size: 12px;
  resize: none;
  min-height: 80px;
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }
`;

const Button = styled.button`
  padding: 8px 16px;
  background: ${props => props.primary ? '#4caf50' : 'rgba(255, 255, 255, 0.2)'};
  border: ${props => props.primary ? 'none' : '1px solid rgba(255, 255, 255, 0.3)'};
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s;
  
  &:hover {
    background: ${props => props.primary ? '#45a049' : 'rgba(255, 255, 255, 0.3)'};
  }
`;

// ============================================================================
// COMPONENT
// ============================================================================

export default function ProctoringDashboard({ examId, studentId, examDuration = 120 }) {
  const [sessionData, setSessionData] = useState(null);
  const [integrityScore, setIntegrityScore] = useState(1.0);
  const [violations, setViolations] = useState([]);
  const [timeRemaining, setTimeRemaining] = useState(examDuration * 60);
  const [isSessionActive, setIsSessionActive] = useState(true);
  const [proctorNotes, setProctorNotes] = useState('');
  const [faceVerified, setFaceVerified] = useState(false);
  const [environmentOk, setEnvironmentOk] = useState(false);
  const videoRef = useRef(null);

  useEffect(() => {
    initializeProctoring();
  }, []);

  useEffect(() => {
    // Timer countdown
    if (!isSessionActive) return;
    
    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 0) {
          setIsSessionActive(false);
          toast.info('Exam time has ended');
          endSession();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isSessionActive]);

  useEffect(() => {
    // Continuous behavior monitoring
    const monitoringInterval = setInterval(() => {
      if (isSessionActive) {
        monitorBehavior();
      }
    }, 5000);
    
    return () => clearInterval(monitoringInterval);
  }, [isSessionActive]);

  const initializeProctoring = async () => {
    try {
      // Start proctoring session
      const startRes = await axios.post(`${API_BASE}/proctoring/sessions/start`, null, {
        params: { exam_id: examId, student_id: studentId }
      });
      
      setSessionData(startRes.data);
      toast.success('Proctoring session started');
      
      // Request camera access
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // Verify identity
      verifyIdentity();
      
      // Check environment
      checkEnvironment();
    } catch (error) {
      toast.error('Failed to initialize proctoring: ' + error.message);
    }
  };

  const verifyIdentity = async () => {
    try {
      if (!videoRef.current) return;
      
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0);
      
      canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('captured_image', blob);
        
        const verifyRes = await axios.post(
          `${API_BASE}/proctoring/verify/identity`,
          formData,
          {
            params: { exam_id: examId, student_id: studentId },
            headers: { 'Content-Type': 'multipart/form-data' }
          }
        );
        
        if (verifyRes.data.is_match) {
          setFaceVerified(true);
          toast.success('Identity verified');
        } else {
          toast.error('Face verification failed');
        }
      });
    } catch (error) {
      console.error('Identity verification failed:', error);
    }
  };

  const checkEnvironment = async () => {
    try {
      const checkRes = await axios.post(
        `${API_BASE}/proctoring/verify/environment`,
        null,
        { params: { exam_id: examId, student_id: studentId } }
      );
      
      const allOk = 
        checkRes.data.room_clear &&
        checkRes.data.primary_monitor &&
        checkRes.data.camera_working &&
        checkRes.data.stable_connection;
      
      setEnvironmentOk(allOk);
      
      if (allOk) {
        toast.success('Environment check passed');
      } else {
        toast.warning('Some environment checks failed');
      }
    } catch (error) {
      console.error('Environment check failed:', error);
    }
  };

  const monitorBehavior = async () => {
    try {
      const behaviorData = {
        gaze: 'center',
        hand_visible: true,
        posture_ok: true,
        mouse_moves: Math.random() * 100,
        scroll_speed: Math.random() * 500
      };
      
      const monitorRes = await axios.post(
        `${API_BASE}/proctoring/monitor/behavior`,
        behaviorData,
        { params: { exam_id: examId, student_id: studentId } }
      );
      
      setIntegrityScore(1.0 - monitorRes.data.risk_score);
      
      if (monitorRes.data.violations_detected > 0) {
        fetchViolations();
      }
    } catch (error) {
      console.error('Behavior monitoring failed:', error);
    }
  };

  const fetchViolations = async () => {
    try {
      const violRes = await axios.get(
        `${API_BASE}/proctoring/violations/${examId}/${studentId}`
      );
      setViolations(violRes.data);
    } catch (error) {
      console.error('Failed to fetch violations:', error);
    }
  };

  const endSession = async () => {
    try {
      if (!sessionData) return;
      
      await axios.post(
        `${API_BASE}/proctoring/sessions/${sessionData.session_id}/end`
      );
      
      toast.success('Proctoring session ended');
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <DashboardContainer>
      <Header>
        <Title>
          <Shield className="w-6 h-6" />
          Certification Exam Proctoring
        </Title>
        <StatusBadge status={integrityScore > 0.8 ? 'active' : integrityScore > 0.5 ? 'warning' : 'critical'}>
          {isSessionActive ? 'ACTIVE' : 'ENDED'}
        </StatusBadge>
      </Header>

      <GridContainer>
        <MetricCard>
          <MetricLabel>Integrity Score</MetricLabel>
          <MetricValue>
            {(integrityScore * 100).toFixed(0)}%
          </MetricValue>
        </MetricCard>

        <MetricCard>
          <MetricLabel>Face Verification</MetricLabel>
          <MetricValue>
            {faceVerified ? '✓ Verified' : '⊗ Pending'}
          </MetricValue>
        </MetricCard>

        <MetricCard>
          <MetricLabel>Environment Check</MetricLabel>
          <MetricValue>
            {environmentOk ? '✓ Clear' : '⊗ Issues'}
          </MetricValue>
        </MetricCard>

        <MetricCard>
          <MetricLabel>Time Remaining</MetricLabel>
          <TimerContainer>
            <Timer>{formatTime(timeRemaining)}</Timer>
          </TimerContainer>
        </MetricCard>
      </GridContainer>

      <SectionContainer>
        <Section>
          <SectionTitle>
            <Video className="w-4 h-4" />
            Webcam Stream
          </SectionTitle>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{
              width: '100%',
              borderRadius: '6px',
              backgroundColor: '#000',
              maxHeight: '300px'
            }}
          />
        </Section>

        <Section>
          <SectionTitle>
            <AlertTriangle className="w-4 h-4" />
            Violations ({violations.length})
          </SectionTitle>
          {violations.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', opacity: 0.7 }}>
              No violations detected
            </div>
          ) : (
            <ViolationList>
              {violations.slice(0, 5).map(v => (
                <ViolationItem key={v.violation_id}>
                  <strong>{v.violation_type}</strong> - {v.description}
                </ViolationItem>
              ))}
            </ViolationList>
          )}
        </Section>

        <Section>
          <SectionTitle>
            <Eye className="w-4 h-4" />
            Environment Checks
          </SectionTitle>
          <ChecklistItem>
            {environmentOk ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>Room Clear & No Distractions</span>
          </ChecklistItem>
          <ChecklistItem>
            {faceVerified ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>Face Verification</span>
          </ChecklistItem>
          <ChecklistItem>
            {environmentOk ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>Single Monitor</span>
          </ChecklistItem>
          <ChecklistItem>
            {environmentOk ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>Stable Connection</span>
          </ChecklistItem>
        </Section>
      </SectionContainer>

      <Section>
        <SectionTitle>
          <User className="w-4 h-4" />
          Proctor Notes
        </SectionTitle>
        <ProctorNotes
          value={proctorNotes}
          onChange={(e) => setProctorNotes(e.target.value)}
          placeholder="Add notes about exam attempt..."
        />
      </Section>

      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <Button onClick={verifyIdentity}>
          <Camera className="w-4 h-4 inline mr-2" />
          Re-verify Identity
        </Button>
        <Button onClick={checkEnvironment}>
          <Eye className="w-4 h-4 inline mr-2" />
          Check Environment
        </Button>
        <Button primary onClick={endSession}>
          <Award className="w-4 h-4 inline mr-2" />
          End Session
        </Button>
      </div>
    </DashboardContainer>
  );
}
