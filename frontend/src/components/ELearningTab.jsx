import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { BookOpen, Plus, Users, Award, TrendingUp, Play } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

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

const CourseLevel = styled.span`
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin: 10px 0;
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

const ELearningTab = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    level: 'beginner',
    price: '0'
  });

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000/api';
  const token = localStorage.getItem('gaaius_token');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/v1/elearning/courses`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourses(response.data.courses || []);
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

  return (
    <Container>
      <Header>
        <Title>
          <BookOpen size={32} />
          E-Learning Platform
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
                color: 'black'
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
                minHeight: '80px'
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
                color: 'black'
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
                color: 'black'
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
              Create your first course to get started!
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
              <Button style={{ marginTop: '15px', width: '100%', marginRight: '0' }}>
                <Play size={14} style={{ display: 'inline', marginRight: '5px' }} />
                Manage Course
              </Button>
            </Card>
          ))
        )}
      </GridContainer>
    </Container>
  );
};

export default ELearningTab;
