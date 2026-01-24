import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  BookOpen, Plus, Users, Award, TrendingUp, Play, Brain, Zap,
  ChevronRight, AlertCircle, CheckCircle, Clock, Target
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
  border-radius: 12px;
  overflow-y: auto;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  justify-content: space-between;
`;

const Title = styled.h2`
  font-size: 28px;
  color: white;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const TitleBadge = styled.span`
  background: rgba(76, 175, 80, 0.3);
  border: 1px solid rgba(76, 175, 80, 0.6);
  color: #4caf50;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
`;

const TabContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
`;

const Tab = styled.button`
  background: none;
  border: none;
  color: ${props => props.active ? 'white' : 'rgba(255, 255, 255, 0.6)'};
  padding: 10px 20px;
  cursor: pointer;
  font-size: 16px;
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  border-bottom: ${props => props.active ? '3px solid white' : 'none'};
  transition: all 0.3s ease;

  &:hover {
    color: white;
  }
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

const AdaptiveCard = styled(Card)`
  border: 1px solid rgba(76, 175, 80, 0.4);
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(33, 150, 243, 0.1) 100%);

  &:hover {
    border: 1px solid rgba(76, 175, 80, 0.6);
    box-shadow: 0 10px 30px rgba(76, 175, 80, 0.2);
  }
`;

const CourseLevel = styled.span`
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin: 10px 0;
`;

const AdaptiveLevel = styled(CourseLevel)`
  background: rgba(76, 175, 80, 0.3);
  color: #4caf50;
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
  margin-right: 10px;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`;

const PrimaryButton = styled(Button)`
  background: rgba(76, 175, 80, 0.3);
  border: 1px solid rgba(76, 175, 80, 0.6);
  color: #4caf50;

  &:hover {
    background: rgba(76, 175, 80, 0.4);
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

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  width: ${props => props.percentage}%;
  transition: width 0.3s ease;
`;

const RecommendationBadge = styled.span`
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
  margin-top: 8px;
  background: ${props => {
    switch(props.type) {
      case 'challenge': return 'rgba(255, 152, 0, 0.3)';
      case 'review': return 'rgba(244, 67, 54, 0.3)';
      case 'next': return 'rgba(76, 175, 80, 0.3)';
      default: return 'rgba(255, 255, 255, 0.2)';
    }
  }};
  color: ${props => {
    switch(props.type) {
      case 'challenge': return '#ffb74d';
      case 'review': return '#ef5350';
      case 'next': return '#4caf50';
      default: return 'white';
    }
  }};
`;

const WeakAreaAlert = styled.div`
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid rgba(244, 67, 54, 0.5);
  border-radius: 8px;
  padding: 12px;
  color: #ef5350;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  font-size: 13px;
`;

const SuccessAlert = styled(WeakAreaAlert)`
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.5);
  color: #4caf50;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
`;

const MetricCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  color: white;
`;

const MetricValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #4caf50;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 5px;
`;

// ============================================================================
// ADAPTIVE ELEARNING TAB COMPONENT
// ============================================================================

const AdaptiveELearningTab = () => {
  // State
  const [courses, setCourses] = useState([]);
  const [learningPaths, setLearningPaths] = useState({});
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeTab, setActiveTab] = useState('courses');
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courseProgress, setCourseProgress] = useState(null);
  const [weakAreas, setWeakAreas] = useState([]);
  const [strongAreas, setStrongAreas] = useState([]);
  const [nextRecommendation, setNextRecommendation] = useState(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    level: 'beginner',
    price: '0'
  });

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const ADAPTIVE_API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  const token = localStorage.getItem('gaaius_token');
  const studentId = localStorage.getItem('gaaius_student_id') || 'default_student';

  // Effects
  useEffect(() => {
    fetchCourses();
  }, []);

  // API Calls
  const fetchCourses = async () => {
    try {
      setLoading(true);
      // Try to fetch from actual eLearning API
      try {
        const response = await axios.get(`${API_BASE}/v1/courses`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setCourses(response.data.courses || response.data || []);
      } catch (error1) {
        // Fallback to mock courses if API not available
        console.warn('Using mock courses, eLearning API not available');
        setCourses([
          {
            id: 'course-1',
            title: 'Python Fundamentals',
            description: 'Learn Python programming from scratch',
            instructor: 'Jane Smith',
            level: 'beginner',
            price: 29.99,
            students_enrolled: 342,
            rating: 4.8,
            lessons: [
              { id: 'l1', title: 'Introduction to Python', lesson_number: 1 },
              { id: 'l2', title: 'Variables and Data Types', lesson_number: 2 },
              { id: 'l3', title: 'Control Flow', lesson_number: 3 },
              { id: 'l4', title: 'Functions', lesson_number: 4 },
              { id: 'l5', title: 'OOP Basics', lesson_number: 5 }
            ]
          },
          {
            id: 'course-2',
            title: 'Web Development Essentials',
            description: 'Master HTML, CSS, and JavaScript',
            instructor: 'John Doe',
            level: 'intermediate',
            price: 49.99,
            students_enrolled: 512,
            rating: 4.9,
            lessons: [
              { id: 'l6', title: 'HTML Basics', lesson_number: 1 },
              { id: 'l7', title: 'CSS Styling', lesson_number: 2 },
              { id: 'l8', title: 'JavaScript Fundamentals', lesson_number: 3 }
            ]
          },
          {
            id: 'course-3',
            title: 'Data Science with Python',
            description: 'Learn data analysis and visualization',
            instructor: 'Sarah Johnson',
            level: 'advanced',
            price: 79.99,
            students_enrolled: 201,
            rating: 4.7,
            lessons: [
              { id: 'l9', title: 'NumPy Basics', lesson_number: 1 },
              { id: 'l10', title: 'Pandas for Data Analysis', lesson_number: 2 }
            ]
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_BASE}/v1/elearning/courses`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Course created successfully!');
      setFormData({ title: '', description: '', level: 'beginner', price: '0' });
      setShowCreateForm(false);
      fetchCourses();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create course');
    }
  };

  const handleEnrollCourse = async (courseId) => {
    try {
      setLoading(true);
      const course = courses.find(c => c.id === courseId);
      const lessonCount = course?.lessons?.length || 15;
      const contentTypes = course?.lessons?.map(l => l.title) || ['module-1', 'module-2', 'module-3'];

      // First, enroll in the course via eLearning API
      try {
        await axios.post(
          `${API_BASE}/v1/courses/${courseId}/enroll`,
          { user_id: studentId },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } catch (enrollError) {
        console.warn('eLearning enrollment API not available, proceeding with adaptive path');
      }

      // Create adaptive learning path via integrated endpoint
      const pathResponse = await axios.post(
        `${API_BASE}/v1/courses/${courseId}/adaptive-path/create`,
        {},
        {
          params: {
            user_id: studentId,
            starting_level: course?.level || 'beginner'
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const pathId = pathResponse.data.path_id;
      
      // Fetch progress and analytics
      const [analyticsRes, weakRes, strongRes] = await Promise.all([
        axios.get(`${API_BASE}/v1/courses/${courseId}/adaptive-path/${pathId}/analytics`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE}/v1/courses/${courseId}/adaptive-path/${pathId}/weak-areas`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_BASE}/v1/courses/${courseId}/adaptive-path/${pathId}/strong-areas`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setLearningPaths(prev => ({ ...prev, [courseId]: pathId }));
      setCourseProgress(analyticsRes.data);
      setWeakAreas(weakRes.data.weak_areas || []);
      setStrongAreas(strongRes.data.strong_areas || []);
      setSelectedCourse(courseId);
      setActiveTab('progress');

      toast.success('Enrolled in course! Your adaptive learning path has been created.');
    } catch (error) {
      console.error('Enrollment error:', error);
      toast.error(error.response?.data?.detail || 'Failed to enroll in course');
    } finally {
      setLoading(false);
    }
  };

  const handleRequestTutoring = async (topic) => {
    try {
      const pathId = learningPaths[selectedCourse];
      if (!pathId) {
        toast.error('Please enroll in a course first');
        return;
      }
      
      // Link tutoring session to learning path via integrated endpoint
      await axios.post(
        `${API_BASE}/v1/courses/${selectedCourse}/adaptive-path/${pathId}/ai-tutoring-link`,
        {},
        {
          params: {
            tutoring_session_id: `tut_${Date.now()}`,
            topic: topic,
            duration_minutes: 30
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast.success(`AI Tutoring session started for: ${topic}`);
      // Navigate to AI Tutoring would go here
    } catch (error) {
      console.error('Tutoring error:', error);
      toast.error('Failed to start tutoring session');
    }
  };

  const handleViewRecommendation = async () => {
    try {
      const pathId = learningPaths[selectedCourse];
      if (!pathId) {
        toast.error('Please enroll in a course first');
        return;
      }

      // Fetch recommendations from integrated endpoint
      const response = await axios.get(
        `${API_BASE}/v1/courses/${selectedCourse}/adaptive-path/${pathId}/recommendations`,
        {
          params: { last_quiz_score: 0.75 },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setNextRecommendation(response.data.recommendations?.[0]);
      toast.success('Next recommendation loaded!');
    } catch (error) {
      console.error('Recommendation error:', error);
      toast.error('Failed to load recommendation');
    }
  };

  // Render Methods
  const renderCoursesTab = () => (
    <>
      <Header>
        <Title>
          <BookOpen size={32} />
          E-Learning Platform
          <TitleBadge>ADAPTIVE</TitleBadge>
        </Title>
        <Button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : '+ New Course'}
        </Button>
      </Header>

      {showCreateForm && (
        <Card style={{ background: 'rgba(255, 255, 255, 0.15)' }}>
          <form onSubmit={handleCreateCourse}>
            <input
              type="text"
              placeholder="Course Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black',
                boxSizing: 'border-box'
              }}
              required
            />
            <textarea
              placeholder="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black',
                minHeight: '80px',
                boxSizing: 'border-box'
              }}
            />
            <select
              value={formData.level}
              onChange={(e) => setFormData({ ...formData, level: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black',
                boxSizing: 'border-box'
              }}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
            <input
              type="number"
              placeholder="Price (0 for free)"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              style={{
                width: '100%',
                padding: '10px',
                marginBottom: '10px',
                borderRadius: '8px',
                border: 'none',
                color: 'black',
                boxSizing: 'border-box'
              }}
            />
            <Button type="submit" style={{ background: 'rgba(59, 130, 246, 0.3)', marginRight: '0' }}>
              Create Course
            </Button>
          </form>
        </Card>
      )}

      <GridContainer>
        {courses.length === 0 && !loading ? (
          <Card style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
            <Title style={{ fontSize: '20px', justifyContent: 'center' }}>
              <BookOpen size={24} />
              No Courses Yet
            </Title>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              Create your first course to get started with adaptive learning!
            </p>
          </Card>
        ) : (
          courses.map((course) => (
            <Card key={course.course_id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3 style={{ margin: '0 0 10px 0' }}>{course.title}</h3>
                  <CourseLevel>{course.level || 'Beginner'}</CourseLevel>
                </div>
              </div>
              <StatRow>
                <span>
                  <Users size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Students: {course.students_count || 0}
                </span>
              </StatRow>
              <StatRow>
                <span>
                  <Award size={16} style={{ display: 'inline', marginRight: '5px' }} />
                  Rating: {course.rating || 'N/A'}
                </span>
              </StatRow>
              <StatRow>
                <span>Lessons: {course.lessons_count || 0}</span>
              </StatRow>
              <StatRow style={{ marginTop: '15px' }}>
                <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
                  ${course.price || 'Free'}
                </span>
              </StatRow>
              <PrimaryButton
                style={{ marginTop: '15px', width: '100%' }}
                onClick={() => handleEnrollCourse(course.course_id)}
              >
                <Brain size={16} />
                Start Adaptive Learning
              </PrimaryButton>
            </Card>
          ))
        )}
      </GridContainer>
    </>
  );

  const renderProgressTab = () => {
    if (!selectedCourse) {
      return (
        <Card style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
          <Title style={{ fontSize: '20px', justifyContent: 'center' }}>
            <BookOpen size={24} />
            Select a Course
          </Title>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Enroll in a course to see your adaptive learning progress.
          </p>
        </Card>
      );
    }

    return (
      <>
        <Header>
          <Title>
            <TrendingUp size={32} />
            Your Learning Progress
          </Title>
          <Button onClick={() => setActiveTab('courses')}>← Back</Button>
        </Header>

        {/* Metrics */}
        {courseProgress && (
          <MetricsGrid>
            <MetricCard>
              <MetricValue>{courseProgress.completion_percentage?.toFixed(1)}%</MetricValue>
              <MetricLabel>Completion</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{courseProgress.average_quiz_score?.toFixed(2)}</MetricValue>
              <MetricLabel>Avg Score</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{courseProgress.completed_lessons || 0}</MetricValue>
              <MetricLabel>Lessons Done</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{courseProgress.total_lessons || 0}</MetricValue>
              <MetricLabel>Total Lessons</MetricLabel>
            </MetricCard>
          </MetricsGrid>
        )}

        {/* Weak Areas */}
        {weakAreas.length > 0 && (
          <WeakAreaAlert>
            <AlertCircle size={20} />
            <div>
              <strong>Weak Areas:</strong> {weakAreas.join(', ')}
              <br />
              <small>Need help? Click request tutoring below.</small>
            </div>
          </WeakAreaAlert>
        )}

        {/* Strong Areas */}
        {strongAreas.length > 0 && (
          <SuccessAlert>
            <CheckCircle size={20} />
            <div>
              <strong>Mastered:</strong> {strongAreas.join(', ')}
            </div>
          </SuccessAlert>
        )}

        {/* Next Recommendation */}
        {nextRecommendation && (
          <AdaptiveCard>
            <h3 style={{ margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Target size={20} />
              Next Recommended Lesson
            </h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
              <strong>{nextRecommendation.lesson_title}</strong>
            </p>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '14px' }}>
              {nextRecommendation.reason}
            </p>
            <RecommendationBadge type={nextRecommendation.recommendation_type}>
              {nextRecommendation.recommendation_type.toUpperCase()}
            </RecommendationBadge>
            <div style={{ marginTop: '15px', fontSize: '12px', color: 'rgba(255, 255, 255, 0.6)' }}>
              <Clock size={14} style={{ display: 'inline', marginRight: '5px' }} />
              Est. {nextRecommendation.estimated_duration} minutes
            </div>
            <Button style={{ marginTop: '15px', width: '100%' }}>
              <Play size={14} />
              Start Lesson
            </Button>
          </AdaptiveCard>
        )}

        {/* Tutoring Support */}
        {weakAreas.length > 0 && (
          <Card>
            <h3 style={{ margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Brain size={20} />
              Get AI Tutoring Help
            </h3>
            <p style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '14px', marginBottom: '15px' }}>
              Request one-on-one AI tutoring for your weak areas:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
              {weakAreas.map(area => (
                <PrimaryButton
                  key={area}
                  onClick={() => handleRequestTutoring(area)}
                  style={{ margin: '0' }}
                >
                  <Zap size={14} />
                  Tutor: {area}
                </PrimaryButton>
              ))}
            </div>
          </Card>
        )}

        {!nextRecommendation && (
          <Button onClick={handleViewRecommendation} style={{ width: '100%', marginBottom: '20px' }}>
            <ChevronRight size={16} />
            Load Next Recommendation
          </Button>
        )}
      </>
    );
  };

  // Main Render
  return (
    <Container>
      <TabContainer>
        <Tab active={activeTab === 'courses'} onClick={() => setActiveTab('courses')}>
          <BookOpen size={18} style={{ display: 'inline', marginRight: '8px' }} />
          Courses
        </Tab>
        <Tab active={activeTab === 'progress'} onClick={() => setActiveTab('progress')}>
          <TrendingUp size={18} style={{ display: 'inline', marginRight: '8px' }} />
          My Progress
        </Tab>
      </TabContainer>

      {activeTab === 'courses' && renderCoursesTab()}
      {activeTab === 'progress' && renderProgressTab()}

      {loading && (
        <Card style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
          <p>Loading...</p>
        </Card>
      )}
    </Container>
  );
};

export default AdaptiveELearningTab;
