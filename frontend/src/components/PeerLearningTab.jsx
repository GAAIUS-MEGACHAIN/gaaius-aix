import React, { useState, useEffect, useCallback } from "react";
import styled from "styled-components";
import { 
  Users, MessageSquare, BookOpen, Award, Heart, Share2, Clock, 
  Plus, Search, Filter, ChevronRight, Star, Zap, Trophy, TrendingUp,
  Send, Link as LinkIcon, Download, Eye, ThumbsUp, MessageCircle,
  Calendar, User, LogOut, MoreVertical, CheckCircle, AlertCircle,
  Loader2, X, Edit, Save, Trash2
} from "lucide-react";
import axios from "axios";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

// ============================================================================
// STYLED COMPONENTS
// ============================================================================

const Container = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  font-family: 'Inter', sans-serif;
`;

const Sidebar = styled.div`
  width: 280px;
  background: rgba(15, 15, 25, 0.95);
  border-right: 1px solid rgba(100, 200, 255, 0.1);
  overflow-y: auto;
  padding: 20px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(100, 200, 255, 0.05);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(100, 200, 255, 0.3);
    border-radius: 3px;
  }
`;

const SidebarTitle = styled.h2`
  font-size: 14px;
  font-weight: 600;
  color: rgba(100, 200, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 20px 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(100, 200, 255, 0.1);
`;

const NavItem = styled.div`
  padding: 12px 12px;
  margin: 4px 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  background: ${props => props.active ? "rgba(100, 200, 255, 0.2)" : "transparent"};
  color: ${props => props.active ? "#64c8ff" : "rgba(200, 200, 200, 0.7)"};
  border: 1px solid ${props => props.active ? "rgba(100, 200, 255, 0.3)" : "transparent"};
  
  &:hover {
    background: rgba(100, 200, 255, 0.1);
    color: #64c8ff;
  }
  
  svg {
    width: 18px;
    height: 18px;
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: rgba(10, 10, 20, 0.6);
  border-bottom: 1px solid rgba(100, 200, 255, 0.1);
`;

const Title = styled.h1`
  font-size: 28px;
  font-weight: 700;
  color: #64c8ff;
  margin: 0;
`;

const ActionButton = styled.button`
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #64c8ff 0%, #4a9fd8 100%);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(100, 200, 255, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ContentArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(100, 200, 255, 0.05);
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(100, 200, 255, 0.3);
    border-radius: 4px;
  }
`;

const TabContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(100, 200, 255, 0.1);
`;

const TabButton = styled.button`
  padding: 12px 20px;
  background: none;
  border: none;
  color: ${props => props.active ? "#64c8ff" : "rgba(200, 200, 200, 0.6)"};
  font-weight: ${props => props.active ? "600" : "500"};
  cursor: pointer;
  border-bottom: 3px solid ${props => props.active ? "#64c8ff" : "transparent"};
  transition: all 0.3s ease;
  
  &:hover {
    color: #64c8ff;
  }
`;

const Card = styled.div`
  background: rgba(20, 20, 40, 0.8);
  border: 1px solid rgba(100, 200, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(100, 200, 255, 0.4);
    background: rgba(20, 20, 40, 0.95);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const CardTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: #64c8ff;
  margin: 0;
`;

const CardDescription = styled.p`
  font-size: 13px;
  color: rgba(200, 200, 200, 0.6);
  margin: 8px 0 0 0;
`;

const Badge = styled.span`
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => {
    switch(props.type) {
      case "mentor": return "rgba(100, 200, 100, 0.2)";
      case "active": return "rgba(100, 200, 255, 0.2)";
      case "completed": return "rgba(150, 100, 255, 0.2)";
      case "pending": return "rgba(255, 150, 100, 0.2)";
      default: return "rgba(100, 200, 255, 0.2)";
    }
  }};
  color: ${props => {
    switch(props.type) {
      case "mentor": return "#64c864";
      case "active": return "#64c8ff";
      case "completed": return "#b464ff";
      case "pending": return "#ff9664";
      default: return "#64c8ff";
    }
  }};
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin: 20px 0;
`;

const StatCard = styled.div`
  background: rgba(30, 30, 50, 0.8);
  border: 1px solid rgba(100, 200, 255, 0.1);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  
  .label {
    font-size: 12px;
    color: rgba(200, 200, 200, 0.6);
    margin-bottom: 8px;
  }
  
  .value {
    font-size: 24px;
    font-weight: 700;
    color: #64c8ff;
  }
`;

const InputField = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(100, 200, 255, 0.2);
  border-radius: 8px;
  background: rgba(20, 20, 40, 0.8);
  color: #fff;
  font-size: 14px;
  margin-bottom: 12px;
  
  &:focus {
    outline: none;
    border-color: rgba(100, 200, 255, 0.6);
    box-shadow: 0 0 12px rgba(100, 200, 255, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid rgba(100, 200, 255, 0.2);
  border-radius: 8px;
  background: rgba(20, 20, 40, 0.8);
  color: #fff;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  min-height: 100px;
  resize: vertical;
  margin-bottom: 12px;
  
  &:focus {
    outline: none;
    border-color: rgba(100, 200, 255, 0.6);
    box-shadow: 0 0 12px rgba(100, 200, 255, 0.1);
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: rgba(200, 200, 200, 0.6);
  
  svg {
    width: 48px;
    height: 48px;
    margin-bottom: 20px;
    opacity: 0.5;
  }
  
  p {
    font-size: 14px;
    margin: 0;
  }
`;

// ============================================================================
// PEER LEARNING COMPONENT
// ============================================================================

export default function PeerLearningTab() {
  const [activeTab, setActiveTab] = useState("study-groups");
  const [studyGroups, setStudyGroups] = useState([]);
  const [discussions, setDiscussions] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [stats, setStats] = useState({});

  // Form states
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    subject: "",
    level: "beginner",
    goals: ""
  });

  // Load data on mount
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // Mock user ID - in production, get from auth
      const userId = "user123";
      
      // Load study groups
      const groupsRes = await axios.get(`${API}/peer-learning/study-groups`);
      setStudyGroups(groupsRes.data.groups || []);
      
      // Load discussions
      const discussionsRes = await axios.get(`${API}/peer-learning/discussions/threads`);
      setDiscussions(discussionsRes.data.threads || []);
      
      // Load user profile
      const profileRes = await axios.get(`${API}/peer-learning/profile/${userId}`);
      setUserProfile(profileRes.data.profile);
      setStats(profileRes.data.collaboration_stats);
      
      // Load mentors
      const mentorsRes = await axios.get(`${API}/peer-learning/mentorship/mentors?topic=machine-learning`);
      setMentors(mentorsRes.data.mentors || []);
    } catch (error) {
      console.error("Error loading data:", error);
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const createStudyGroup = async () => {
    if (!formData.name || !formData.description || !formData.subject) {
      toast.error("Please fill in all required fields");
      return;
    }

    try {
      const response = await axios.post(`${API}/peer-learning/study-groups/create`, {
        ...formData,
        creator_id: "user123",
        course_id: "course123",
        max_members: 15,
        goals: formData.goals ? formData.goals.split(",") : []
      });

      setStudyGroups([...studyGroups, response.data.group]);
      setShowCreateGroup(false);
      setFormData({ name: "", description: "", subject: "", level: "beginner", goals: "" });
      toast.success("Study group created successfully");
    } catch (error) {
      console.error("Error creating group:", error);
      toast.error("Failed to create study group");
    }
  };

  const joinStudyGroup = async (groupId) => {
    try {
      const response = await axios.post(
        `${API}/peer-learning/study-groups/${groupId}/members/add`,
        { user_id: "user123" }
      );
      toast.success("Joined study group successfully");
      setSelectedGroup(groupId);
      loadInitialData();
    } catch (error) {
      console.error("Error joining group:", error);
      toast.error("Failed to join study group");
    }
  };

  return (
    <Container>
      {/* Sidebar */}
      <Sidebar>
        <div style={{ fontSize: "18px", fontWeight: "700", color: "#64c8ff", marginBottom: "20px" }}>
          👥 Peer Learning
        </div>

        <SidebarTitle>Navigation</SidebarTitle>
        <NavItem active={activeTab === "study-groups"} onClick={() => setActiveTab("study-groups")}>
          <Users size={18} /> Study Groups
        </NavItem>
        <NavItem active={activeTab === "discussions"} onClick={() => setActiveTab("discussions")}>
          <MessageSquare size={18} /> Discussions
        </NavItem>
        <NavItem active={activeTab === "mentorship"} onClick={() => setActiveTab("mentorship")}>
          <Award size={18} /> Mentorship
        </NavItem>
        <NavItem active={activeTab === "resources"} onClick={() => setActiveTab("resources")}>
          <Share2 size={18} /> Resources
        </NavItem>
        <NavItem active={activeTab === "profile"} onClick={() => setActiveTab("profile")}>
          <User size={18} /> My Profile
        </NavItem>

        <SidebarTitle>Statistics</SidebarTitle>
        <StatCard>
          <div className="label">Reputation</div>
          <div className="value">{stats.reputation_score || 0}</div>
        </StatCard>
        <StatCard>
          <div className="label">Achievements</div>
          <div className="value">{stats.achievements || 0}</div>
        </StatCard>
        <StatCard>
          <div className="label">Study Groups</div>
          <div className="value">{stats.study_groups || 0}</div>
        </StatCard>
      </Sidebar>

      {/* Main Content */}
      <MainContent>
        <Header>
          <Title>
            {activeTab === "study-groups" && "Study Groups"}
            {activeTab === "discussions" && "Discussions"}
            {activeTab === "mentorship" && "Find Mentors"}
            {activeTab === "resources" && "Shared Resources"}
            {activeTab === "profile" && "My Profile"}
          </Title>
          {activeTab === "study-groups" && (
            <ActionButton onClick={() => setShowCreateGroup(!showCreateGroup)}>
              <Plus size={18} /> Create Group
            </ActionButton>
          )}
        </Header>

        <ContentArea>
          {/* Study Groups Tab */}
          {activeTab === "study-groups" && (
            <div>
              {showCreateGroup && (
                <Card>
                  <CardTitle>Create New Study Group</CardTitle>
                  <div style={{ marginTop: "15px" }}>
                    <InputField
                      placeholder="Group Name"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    />
                    <TextArea
                      placeholder="Group Description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    />
                    <InputField
                      placeholder="Subject"
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    />
                    <InputField
                      placeholder="Goals (comma separated)"
                      value={formData.goals}
                      onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
                    />
                    <select
                      style={{
                        width: "100%",
                        padding: "10px",
                        borderRadius: "8px",
                        border: "1px solid rgba(100, 200, 255, 0.2)",
                        background: "rgba(20, 20, 40, 0.8)",
                        color: "#fff",
                        marginBottom: "12px"
                      }}
                      value={formData.level}
                      onChange={(e) => setFormData({ ...formData, level: e.target.value })}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                    <div style={{ display: "flex", gap: "10px" }}>
                      <ActionButton onClick={createStudyGroup} style={{ flex: 1 }}>
                        <CheckCircle size={16} /> Create
                      </ActionButton>
                      <ActionButton
                        onClick={() => setShowCreateGroup(false)}
                        style={{ flex: 1, background: "rgba(255, 100, 100, 0.5)" }}
                      >
                        <X size={16} /> Cancel
                      </ActionButton>
                    </div>
                  </div>
                </Card>
              )}

              {loading ? (
                <EmptyState>
                  <Loader2 style={{ animation: "spin 2s linear infinite" }} />
                  <p>Loading study groups...</p>
                </EmptyState>
              ) : studyGroups.length === 0 ? (
                <EmptyState>
                  <Users />
                  <p>No study groups yet. Create one to get started!</p>
                </EmptyState>
              ) : (
                studyGroups.map((group) => (
                  <Card key={group.id}>
                    <CardHeader>
                      <div>
                        <CardTitle>{group.name}</CardTitle>
                        <CardDescription>{group.description}</CardDescription>
                      </div>
                      <Badge type="active">{group.level}</Badge>
                    </CardHeader>
                    <div style={{ marginBottom: "12px", fontSize: "13px", color: "rgba(200, 200, 200, 0.7)" }}>
                      <strong>Subject:</strong> {group.subject} • <strong>Members:</strong> {group.max_members}
                    </div>
                    <ActionButton onClick={() => joinStudyGroup(group.id)}>
                      <Users size={16} /> Join Group
                    </ActionButton>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* Discussions Tab */}
          {activeTab === "discussions" && (
            <div>
              {discussions.length === 0 ? (
                <EmptyState>
                  <MessageSquare />
                  <p>No discussions yet. Start a conversation!</p>
                </EmptyState>
              ) : (
                discussions.map((discussion) => (
                  <Card key={discussion.id}>
                    <CardHeader>
                      <div>
                        <CardTitle>{discussion.title}</CardTitle>
                        <CardDescription>{discussion.description}</CardDescription>
                      </div>
                      <Badge type={discussion.solved ? "completed" : "active"}>
                        {discussion.solved ? "Solved" : "Open"}
                      </Badge>
                    </CardHeader>
                    <div style={{ display: "flex", gap: "15px", fontSize: "12px", color: "rgba(200, 200, 200, 0.6)" }}>
                      <span>💬 {discussion.replies_count} replies</span>
                      <span>👁️ {discussion.views_count} views</span>
                      <span>🏷️ {discussion.tags?.join(", ") || "none"}</span>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* Mentorship Tab */}
          {activeTab === "mentorship" && (
            <div>
              {mentors.length === 0 ? (
                <EmptyState>
                  <Award />
                  <p>No mentors available. Check back later!</p>
                </EmptyState>
              ) : (
                mentors.map((mentor) => (
                  <Card key={mentor.user_id}>
                    <CardHeader>
                      <div>
                        <CardTitle>{mentor.name}</CardTitle>
                        <CardDescription>{mentor.bio}</CardDescription>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "5px", color: "#ffd700" }}>
                        <Trophy size={16} /> {mentor.reputation_score}
                      </div>
                    </CardHeader>
                    <div style={{ marginBottom: "12px", fontSize: "13px", color: "rgba(200, 200, 200, 0.7)" }}>
                      <strong>Expertise:</strong> {mentor.expertise?.join(", ") || "none"}
                    </div>
                    <ActionButton>
                      <MessageSquare size={16} /> Request Mentorship
                    </ActionButton>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* Resources Tab */}
          {activeTab === "resources" && (
            <EmptyState>
              <Share2 />
              <p>Shared resources will appear here</p>
            </EmptyState>
          )}

          {/* Profile Tab */}
          {activeTab === "profile" && userProfile && (
            <div>
              <Card>
                <CardTitle>My Profile</CardTitle>
                <StatGrid>
                  <StatCard>
                    <div className="label">Total Posts</div>
                    <div className="value">{stats.total_posts || 0}</div>
                  </StatCard>
                  <StatCard>
                    <div className="label">Reviews Given</div>
                    <div className="value">{stats.total_reviews_given || 0}</div>
                  </StatCard>
                  <StatCard>
                    <div className="label">Mentorships</div>
                    <div className="value">{stats.total_mentorships || 0}</div>
                  </StatCard>
                  <StatCard>
                    <div className="label">Total Points</div>
                    <div className="value">{stats.total_points || 0}</div>
                  </StatCard>
                </StatGrid>
              </Card>
            </div>
          )}
        </ContentArea>
      </MainContent>
    </Container>
  );
}
