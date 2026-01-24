import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  Shield, CheckCircle, AlertCircle, Clock, Award, FileText,
  Download, Share2, Eye, Lock, Zap
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import ProctoringDashboard from './ProctoringDashboard';

/**
 * Certification Exam Interface
 * Integrates proctoring, exam delivery, and certificate issuance
 */

const API_BASE = 'http://localhost:8000/api/v1';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: #f5f5f5;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
`;

const ExamTitle = styled.h1`
  margin: 0;
  font-size: 24px;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const ExamInfo = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
`;

const InfoCard = styled.div`
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
`;

const InfoLabel = styled.div`
  font-size: 12px;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 8px;
`;

const InfoValue = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const ExamContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 20px;
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Question = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
`;

const QuestionNumber = styled.div`
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
  font-weight: bold;
`;

const QuestionText = styled.div`
  font-size: 16px;
  margin-bottom: 15px;
  color: #333;
`;

const OptionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const Option = styled.button`
  padding: 12px;
  background: ${props => props.selected ? '#667eea' : '#f9f9f9'};
  border: 2px solid ${props => props.selected ? '#667eea' : '#e0e0e0'};
  border-radius: 6px;
  color: ${props => props.selected ? 'white' : '#333'};
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    border-color: #667eea;
    background: ${props => props.selected ? '#667eea' : '#f0f0f0'};
  }
`;

const Sidebar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const SidebarCard = styled.div`
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
`;

const SidebarTitle = styled.h3`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const WarningBox = styled.div`
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #856404;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 10px;
`;

const Button = styled.button`
  flex: 1;
  padding: 10px;
  background: ${props => props.primary ? '#667eea' : '#e0e0e0'};
  border: none;
  color: ${props => props.primary ? 'white' : '#333'};
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  
  &:hover {
    background: ${props => props.primary ? '#5568d3' : '#d0d0d0'};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: ${props => {
    switch(props.status) {
      case 'success': return '#4caf50';
      case 'warning': return '#ffc107';
      case 'error': return '#f44336';
      default: return '#2196f3';
    }
  }};
`;

const CertificatePreview = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 30px;
  border-radius: 8px;
  color: white;
  text-align: center;
`;

const CertTitle = styled.h2`
  margin: 0 0 10px 0;
  font-size: 32px;
`;

const CertDetail = styled.div`
  font-size: 14px;
  margin: 8px 0;
  opacity: 0.9;
`;

// ============================================================================
// COMPONENT
// ============================================================================

export default function CertificationExamPage({ examId, courseId }) {
  const [exam, setExam] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showProctoring, setShowProctoring] = useState(true);
  const [examStatus, setExamStatus] = useState('in_progress'); // in_progress, submitted, graded
  const [score, setScore] = useState(null);
  const [certificate, setCertificate] = useState(null);
  const [integrityScore, setIntegrityScore] = useState(1.0);
  const [violations, setViolations] = useState([]);
  const studentId = 'student-' + Math.random().toString(36).substr(2, 9);

  useEffect(() => {
    loadExam();
  }, []);

  const loadExam = async () => {
    try {
      // In production: Load from API
      const mockExam = {
        exam_id: examId,
        title: 'Advanced JavaScript Certification',
        description: 'Comprehensive exam covering ES6+, async/await, and modern frameworks',
        duration_minutes: 120,
        passing_score: 70,
        total_questions: 50,
        proctor_mode: 'hybrid',
        integrity_level: 'high',
        questions: generateMockQuestions(50)
      };
      setExam(mockExam);
    } catch (error) {
      toast.error('Failed to load exam');
    }
  };

  const generateMockQuestions = (count) => {
    const questions = [];
    for (let i = 0; i < count; i++) {
      questions.push({
        id: `q${i + 1}`,
        number: i + 1,
        text: `Question ${i + 1}: What is the correct answer?`,
        options: [
          'Option A: First choice',
          'Option B: Second choice',
          'Option C: Third choice (Correct)',
          'Option D: Fourth choice'
        ],
        correctAnswer: 'Option C: Third choice (Correct)'
      });
    }
    return questions;
  };

  const selectAnswer = (questionId, answer) => {
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const nextQuestion = () => {
    if (currentQuestion < exam.total_questions - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const submitExam = async () => {
    try {
      setExamStatus('submitted');
      
      // Grade exam
      const correctAnswers = Object.entries(selectedAnswers).filter(([id, answer]) => {
        const question = exam.questions.find(q => q.id === id);
        return question && answer === question.correctAnswer;
      }).length;

      const calculatedScore = (correctAnswers / exam.total_questions) * 100;
      setScore(calculatedScore);

      // Submit to backend
      const submitRes = await axios.post(
        `${API_BASE}/proctoring/attempts/${studentId}/submit`,
        { answers: selectedAnswers }
      );

      // Grade exam
      const gradeRes = await axios.post(
        `${API_BASE}/proctoring/attempts/${studentId}/grade`,
        { score: calculatedScore }
      );

      if (calculatedScore >= exam.passing_score) {
        // Issue certificate
        const certRes = await axios.post(
          `${API_BASE}/proctoring/certificates/issue`,
          {
            exam_attempt_id: studentId,
            exam_id: examId,
            student_id: studentId,
            student_name: 'John Doe',
            score: calculatedScore
          }
        );

        setCertificate(certRes.data);
        setExamStatus('graded');
        toast.success('Exam passed! Certificate issued.');
      } else {
        toast.warning(`Exam failed. Score: ${calculatedScore.toFixed(1)}% (Need ${exam.passing_score}%)`);
        setExamStatus('graded');
      }
    } catch (error) {
      toast.error('Failed to submit exam: ' + error.message);
    }
  };

  if (!exam) return <div>Loading exam...</div>;

  if (showProctoring && examStatus === 'in_progress') {
    return (
      <Container>
        <ProctoringDashboard
          examId={examId}
          studentId={studentId}
          examDuration={exam.duration_minutes}
        />
        <Button primary onClick={() => setShowProctoring(false)} style={{ marginTop: '20px' }}>
          Start Exam
        </Button>
      </Container>
    );
  }

  if (examStatus === 'in_progress') {
    const question = exam.questions[currentQuestion];

    return (
      <Container>
        <Header>
          <ExamTitle>
            <Shield className="w-6 h-6" />
            {exam.title}
          </ExamTitle>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <StatusIndicator status="success">
              <Eye className="w-4 h-4" />
              Proctored
            </StatusIndicator>
            <StatusIndicator status="info">
              <Clock className="w-4 h-4" />
              {exam.duration_minutes} min
            </StatusIndicator>
          </div>
        </Header>

        <ExamInfo>
          <InfoCard>
            <InfoLabel>Question</InfoLabel>
            <InfoValue>{currentQuestion + 1}/{exam.total_questions}</InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Answered</InfoLabel>
            <InfoValue>{Object.keys(selectedAnswers).length}/{exam.total_questions}</InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Integrity</InfoLabel>
            <InfoValue style={{ color: integrityScore > 0.8 ? '#4caf50' : '#ffc107' }}>
              {(integrityScore * 100).toFixed(0)}%
            </InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Violations</InfoLabel>
            <InfoValue style={{ color: violations.length > 0 ? '#f44336' : '#4caf50' }}>
              {violations.length}
            </InfoValue>
          </InfoCard>
        </ExamInfo>

        <ExamContent>
          <MainContent>
            <Question>
              <QuestionNumber>Question {question.number} of {exam.total_questions}</QuestionNumber>
              <QuestionText>{question.text}</QuestionText>
              <OptionsList>
                {question.options.map((option, idx) => (
                  <Option
                    key={idx}
                    selected={selectedAnswers[question.id] === option}
                    onClick={() => selectAnswer(question.id, option)}
                  >
                    {option}
                  </Option>
                ))}
              </OptionsList>
            </Question>

            <ButtonGroup>
              <Button onClick={prevQuestion} disabled={currentQuestion === 0}>
                ← Previous
              </Button>
              <Button primary onClick={nextQuestion} disabled={currentQuestion === exam.total_questions - 1}>
                Next →
              </Button>
              <Button
                primary
                onClick={submitExam}
                style={{ backgroundColor: '#4caf50' }}
              >
                Submit Exam
              </Button>
            </ButtonGroup>
          </MainContent>

          <Sidebar>
            <SidebarCard>
              <SidebarTitle>
                <AlertCircle className="w-4 h-4" />
                Exam Rules
              </SidebarTitle>
              <WarningBox>
                ⚠️ This exam is proctored. Suspicious activity may result in disqualification.
              </WarningBox>
              <ul style={{ fontSize: '12px', lineHeight: '1.6', margin: '10px 0', paddingLeft: '20px' }}>
                <li>No tab switching allowed</li>
                <li>No copy/paste permitted</li>
                <li>Face must be visible</li>
                <li>Only one monitor allowed</li>
                <li>No external help</li>
              </ul>
            </SidebarCard>

            <SidebarCard>
              <SidebarTitle>
                <Zap className="w-4 h-4" />
                Progress
              </SidebarTitle>
              <div style={{ height: '200px', background: '#f5f5f5', borderRadius: '4px', padding: '10px' }}>
                <div style={{ fontSize: '12px', marginBottom: '10px' }}>
                  Answered: {Object.keys(selectedAnswers).length}/{exam.total_questions}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '5px' }}>
                  {exam.questions.map((q, idx) => (
                    <div
                      key={idx}
                      onClick={() => setCurrentQuestion(idx)}
                      style={{
                        padding: '8px',
                        background: selectedAnswers[q.id] ? '#4caf50' : '#e0e0e0',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        color: selectedAnswers[q.id] ? 'white' : '#333',
                        textAlign: 'center',
                        fontSize: '11px',
                        fontWeight: 'bold'
                      }}
                    >
                      {idx + 1}
                    </div>
                  ))}
                </div>
              </div>
            </SidebarCard>
          </Sidebar>
        </ExamContent>
      </Container>
    );
  }

  if (examStatus === 'graded' && certificate) {
    return (
      <Container>
        <Header>
          <ExamTitle>
            <CheckCircle className="w-6 h-6" style={{ color: '#4caf50' }} />
            Exam Completed - Certification Issued
          </ExamTitle>
        </Header>

        <ExamInfo>
          <InfoCard>
            <InfoLabel>Score</InfoLabel>
            <InfoValue style={{ color: score >= exam.passing_score ? '#4caf50' : '#f44336' }}>
              {score.toFixed(1)}%
            </InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Status</InfoLabel>
            <InfoValue style={{ color: score >= exam.passing_score ? '#4caf50' : '#f44336' }}>
              {score >= exam.passing_score ? '✓ PASSED' : '✗ FAILED'}
            </InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Grade</InfoLabel>
            <InfoValue>{certificate.grade}</InfoValue>
          </InfoCard>
          <InfoCard>
            <InfoLabel>Certificate ID</InfoLabel>
            <InfoValue style={{ fontSize: '12px' }}>{certificate.certificate_number}</InfoValue>
          </InfoCard>
        </ExamInfo>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
          <div>
            <CertificatePreview>
              <div style={{ borderTop: '2px solid white', borderBottom: '2px solid white', padding: '20px 0' }}>
                <div style={{ fontSize: '12px', marginBottom: '10px', opacity: 0.8 }}>
                  This certifies that
                </div>
                <CertTitle>John Doe</CertTitle>
                <div style={{ fontSize: '14px', marginBottom: '20px' }}>
                  Has successfully completed
                </div>
                <CertDetail>
                  {exam.title}
                </CertDetail>
                <CertDetail>
                  Score: {score.toFixed(1)}% | Certificate Number: {certificate.certificate_number}
                </CertDetail>
                <CertDetail>
                  Issued: {new Date().toLocaleDateString()}
                </CertDetail>
              </div>
            </CertificatePreview>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <SidebarCard>
              <SidebarTitle>
                <Award className="w-4 h-4" />
                Certificate Actions
              </SidebarTitle>
              <ButtonGroup style={{ flexDirection: 'column' }}>
                <Button primary>
                  <Download className="w-4 h-4 inline mr-2" />
                  Download PDF
                </Button>
                <Button>
                  <Share2 className="w-4 h-4 inline mr-2" />
                  Share Certificate
                </Button>
                <Button>
                  <Eye className="w-4 h-4 inline mr-2" />
                  Verify Online
                </Button>
              </ButtonGroup>
            </SidebarCard>

            <SidebarCard>
              <SidebarTitle>
                <FileText className="w-4 h-4" />
                Credential URL
              </SidebarTitle>
              <div style={{
                background: '#f5f5f5',
                padding: '10px',
                borderRadius: '4px',
                fontSize: '11px',
                wordBreak: 'break-all',
                color: '#667eea'
              }}>
                {certificate.credential_url}
              </div>
            </SidebarCard>
          </div>
        </div>
      </Container>
    );
  }

  return <div>Exam Error</div>;
}
