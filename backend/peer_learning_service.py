"""
Peer Learning & Collaboration Service
Real-time collaboration, study groups, peer-to-peer mentoring, and community features
"""

from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import json
from abc import ABC, abstractmethod
import asyncio
from collections import defaultdict

from pydantic import BaseModel, Field, validator

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class CollaborationStatus(str, Enum):
    """Study group status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ParticipantRole(str, Enum):
    """Role in study group"""
    CREATOR = "creator"
    MENTOR = "mentor"
    MEMBER = "member"

class MentorshipStatus(str, Enum):
    """Mentorship status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    DECLINED = "declined"

class DiscussionCategory(str, Enum):
    """Discussion thread category"""
    STUDY = "study"
    PROJECT = "project"
    CAREER = "career"
    SOCIAL = "social"
    RESOURCES = "resources"
    ANNOUNCEMENTS = "announcements"

class PostType(str, Enum):
    """Discussion post type"""
    QUESTION = "question"
    ANSWER = "answer"
    RESOURCE = "resource"
    ANNOUNCEMENT = "announcement"
    DISCUSSION = "discussion"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class UserProfile(BaseModel):
    """Peer learning user profile"""
    user_id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    expertise: List[str] = Field(default_factory=list)  # Topics they're good at
    learning_interests: List[str] = Field(default_factory=list)  # Topics they want to learn
    availability: Dict[str, str] = Field(default_factory=dict)  # Day -> time slots
    timezone: str = "UTC"
    badges: List[str] = Field(default_factory=list)  # Achievement badges
    reputation_score: int = 0
    total_collaborations: int = 0
    study_groups_count: int = 0
    mentor_of_count: int = 0
    mentored_by_count: int = 0
    response_time_avg: float = 0.0  # Average response time in hours
    profile_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StudyGroupMetadata(BaseModel):
    """Study group metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    course_id: str  # Associated eLearning course
    subject: str  # Main topic
    level: str  # beginner, intermediate, advanced
    max_members: int = Field(default=10, ge=2, le=100)
    goals: List[str] = Field(default_factory=list)
    meeting_schedule: Dict[str, Any] = Field(default_factory=dict)  # Recurring meetings
    resources: List[Dict[str, str]] = Field(default_factory=list)  # Shared materials
    status: CollaborationStatus = CollaborationStatus.ACTIVE
    creator_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudyGroupMember(BaseModel):
    """Study group member"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    user_id: str
    role: ParticipantRole = ParticipantRole.MEMBER
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    contribution_score: int = 0  # Based on posts, help given, etc
    attendance_rate: float = 0.0
    is_active: bool = True

class DiscussionThread(BaseModel):
    """Discussion forum thread"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: Optional[str] = None  # None means public forum
    course_id: Optional[str] = None
    title: str = Field(..., min_length=5, max_length=300)
    description: str = Field(default="")
    creator_id: str
    category: DiscussionCategory
    tags: List[str] = Field(default_factory=list)
    replies_count: int = 0
    views_count: int = 0
    solved: bool = False
    pinned: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_reply_at: Optional[datetime] = None

class DiscussionPost(BaseModel):
    """Discussion forum post"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thread_id: str
    creator_id: str
    content: str = Field(..., min_length=5, max_length=10000)
    post_type: PostType
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    votes: int = 0
    is_answer: bool = False
    is_accepted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MentorshipRequest(BaseModel):
    """Mentorship request"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mentee_id: str
    mentor_id: str
    topic: str
    goals: str = Field(..., min_length=10, max_length=1000)
    duration_weeks: int = Field(..., ge=1, le=52)
    frequency: str  # weekly, biweekly, etc
    status: MentorshipStatus = MentorshipStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class MentorshipSession(BaseModel):
    """Individual mentorship session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mentorship_request_id: str
    mentor_id: str
    mentee_id: str
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=15, le=180)
    topic: str
    notes: str = ""
    feedback: Optional[Dict[str, Any]] = None
    completed: bool = False
    meeting_link: Optional[str] = None
    recording_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PeerReview(BaseModel):
    """Peer assignment/project review"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assignment_id: str
    submitter_id: str
    reviewer_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: str = Field(..., min_length=20, max_length=5000)
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    helpful: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class StudySession(BaseModel):
    """Live study session"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: str
    title: str
    topic: str
    creator_id: str
    scheduled_at: datetime
    duration_minutes: int = Field(default=90, ge=15, le=240)
    max_participants: int = Field(default=15, ge=2, le=100)
    meeting_link: Optional[str] = None
    agenda: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    participants: List[str] = Field(default_factory=list)
    recording_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResourceShare(BaseModel):
    """Shared learning resource"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    group_id: Optional[str] = None  # Group specific or global
    user_id: str
    resource_type: str  # document, video, link, quiz, summary, etc
    title: str
    description: str
    resource_url: str
    preview_image: Optional[str] = None
    relevance_tags: List[str] = Field(default_factory=list)
    access_level: str = "public"  # public, group, private
    downloads: int = 0
    rating: float = 0.0
    reviews_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Achievement(BaseModel):
    """Peer learning achievement/badge"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_type: str  # collaborator, mentor, helper, leader, consistent_learner, etc
    badge_name: str
    description: str
    icon_url: str
    points_awarded: int
    earned_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# PEER LEARNING SERVICE
# ============================================================================

class PeerLearningService:
    """Main peer learning and collaboration service"""
    
    def __init__(self):
        # In-memory storage (replace with MongoDB in production)
        self.study_groups: Dict[str, StudyGroupMetadata] = {}
        self.group_members: Dict[str, List[StudyGroupMember]] = defaultdict(list)
        self.discussion_threads: Dict[str, DiscussionThread] = {}
        self.discussion_posts: Dict[str, List[DiscussionPost]] = defaultdict(list)
        self.mentorship_requests: Dict[str, MentorshipRequest] = {}
        self.mentorship_sessions: Dict[str, List[MentorshipSession]] = defaultdict(list)
        self.peer_reviews: Dict[str, List[PeerReview]] = defaultdict(list)
        self.study_sessions: Dict[str, StudySession] = {}
        self.resource_shares: Dict[str, ResourceShare] = {}
        self.achievements: Dict[str, List[Achievement]] = defaultdict(list)
        self.user_profiles: Dict[str, UserProfile] = {}

    # ========== STUDY GROUP MANAGEMENT ==========
    
    async def create_study_group(self, group_data: StudyGroupMetadata) -> StudyGroupMetadata:
        """Create a new study group"""
        if group_data.id in self.study_groups:
            raise ValueError("Study group already exists")
        
        self.study_groups[group_data.id] = group_data
        
        # Add creator as member with mentor role
        creator_member = StudyGroupMember(
            group_id=group_data.id,
            user_id=group_data.creator_id,
            role=ParticipantRole.CREATOR
        )
        self.group_members[group_data.id].append(creator_member)
        
        return group_data

    async def get_study_group(self, group_id: str) -> Optional[StudyGroupMetadata]:
        """Get study group details"""
        return self.study_groups.get(group_id)

    async def update_study_group(self, group_id: str, updates: Dict[str, Any]) -> StudyGroupMetadata:
        """Update study group"""
        if group_id not in self.study_groups:
            raise ValueError("Study group not found")
        
        group = self.study_groups[group_id]
        for key, value in updates.items():
            if hasattr(group, key):
                setattr(group, key, value)
        
        group.updated_at = datetime.utcnow()
        return group

    async def list_study_groups(self, course_id: Optional[str] = None, subject: Optional[str] = None) -> List[StudyGroupMetadata]:
        """List study groups with optional filters"""
        groups = list(self.study_groups.values())
        
        if course_id:
            groups = [g for g in groups if g.course_id == course_id]
        if subject:
            groups = [g for g in groups if g.subject == subject]
        
        return sorted(groups, key=lambda g: g.created_at, reverse=True)

    async def add_member_to_group(self, group_id: str, user_id: str, role: ParticipantRole = ParticipantRole.MEMBER) -> StudyGroupMember:
        """Add member to study group"""
        if group_id not in self.study_groups:
            raise ValueError("Study group not found")
        
        # Check if already member
        existing = [m for m in self.group_members[group_id] if m.user_id == user_id]
        if existing:
            raise ValueError("User is already a member")
        
        # Check capacity
        if len(self.group_members[group_id]) >= self.study_groups[group_id].max_members:
            raise ValueError("Study group is full")
        
        member = StudyGroupMember(group_id=group_id, user_id=user_id, role=role)
        self.group_members[group_id].append(member)
        
        return member

    async def remove_member_from_group(self, group_id: str, user_id: str) -> bool:
        """Remove member from study group"""
        if group_id not in self.group_members:
            return False
        
        self.group_members[group_id] = [m for m in self.group_members[group_id] if m.user_id != user_id]
        return True

    async def get_group_members(self, group_id: str) -> List[StudyGroupMember]:
        """Get all members in a study group"""
        return self.group_members.get(group_id, [])

    async def update_member_role(self, group_id: str, user_id: str, new_role: ParticipantRole) -> StudyGroupMember:
        """Update member role in group"""
        members = self.group_members.get(group_id, [])
        for member in members:
            if member.user_id == user_id:
                member.role = new_role
                return member
        
        raise ValueError("Member not found in group")

    # ========== DISCUSSION FORUM ==========
    
    async def create_discussion_thread(self, thread_data: DiscussionThread) -> DiscussionThread:
        """Create a new discussion thread"""
        self.discussion_threads[thread_data.id] = thread_data
        return thread_data

    async def create_discussion_post(self, post_data: DiscussionPost) -> DiscussionPost:
        """Create a discussion post"""
        if post_data.thread_id not in self.discussion_threads:
            raise ValueError("Thread not found")
        
        self.discussion_posts[post_data.thread_id].append(post_data)
        
        # Update thread metadata
        thread = self.discussion_threads[post_data.thread_id]
        thread.replies_count += 1
        thread.updated_at = datetime.utcnow()
        thread.last_reply_at = datetime.utcnow()
        
        return post_data

    async def get_discussion_thread(self, thread_id: str) -> Optional[DiscussionThread]:
        """Get discussion thread"""
        if thread_id in self.discussion_threads:
            # Increment views
            self.discussion_threads[thread_id].views_count += 1
        return self.discussion_threads.get(thread_id)

    async def get_discussion_posts(self, thread_id: str) -> List[DiscussionPost]:
        """Get all posts in a thread"""
        return self.discussion_posts.get(thread_id, [])

    async def mark_post_as_answer(self, thread_id: str, post_id: str) -> bool:
        """Mark a post as accepted answer"""
        posts = self.discussion_posts.get(thread_id, [])
        for post in posts:
            if post.id == post_id:
                post.is_accepted = True
                thread = self.discussion_threads[thread_id]
                thread.solved = True
                return True
        return False

    async def list_discussion_threads(self, group_id: Optional[str] = None, course_id: Optional[str] = None) -> List[DiscussionThread]:
        """List discussion threads"""
        threads = list(self.discussion_threads.values())
        
        if group_id:
            threads = [t for t in threads if t.group_id == group_id]
        if course_id:
            threads = [t for t in threads if t.course_id == course_id]
        
        return sorted(threads, key=lambda t: t.last_reply_at or t.created_at, reverse=True)

    async def vote_on_post(self, post_id: str, thread_id: str, vote: int) -> int:
        """Vote on a discussion post (upvote/downvote)"""
        posts = self.discussion_posts.get(thread_id, [])
        for post in posts:
            if post.id == post_id:
                post.votes += vote
                return post.votes
        raise ValueError("Post not found")

    # ========== MENTORSHIP ==========
    
    async def create_mentorship_request(self, request_data: MentorshipRequest) -> MentorshipRequest:
        """Create mentorship request"""
        self.mentorship_requests[request_data.id] = request_data
        return request_data

    async def get_mentorship_request(self, request_id: str) -> Optional[MentorshipRequest]:
        """Get mentorship request"""
        return self.mentorship_requests.get(request_id)

    async def accept_mentorship_request(self, request_id: str) -> MentorshipRequest:
        """Accept mentorship request"""
        if request_id not in self.mentorship_requests:
            raise ValueError("Request not found")
        
        request = self.mentorship_requests[request_id]
        request.status = MentorshipStatus.ACTIVE
        request.accepted_at = datetime.utcnow()
        
        return request

    async def decline_mentorship_request(self, request_id: str) -> MentorshipRequest:
        """Decline mentorship request"""
        if request_id not in self.mentorship_requests:
            raise ValueError("Request not found")
        
        request = self.mentorship_requests[request_id]
        request.status = MentorshipStatus.DECLINED
        
        return request

    async def schedule_mentorship_session(self, session_data: MentorshipSession) -> MentorshipSession:
        """Schedule a mentorship session"""
        req_id = session_data.mentorship_request_id
        self.mentorship_sessions[req_id].append(session_data)
        return session_data

    async def get_mentorship_sessions(self, request_id: str) -> List[MentorshipSession]:
        """Get all sessions for a mentorship"""
        return self.mentorship_sessions.get(request_id, [])

    async def complete_mentorship(self, request_id: str) -> MentorshipRequest:
        """Mark mentorship as completed"""
        if request_id not in self.mentorship_requests:
            raise ValueError("Request not found")
        
        request = self.mentorship_requests[request_id]
        request.status = MentorshipStatus.COMPLETED
        request.completed_at = datetime.utcnow()
        
        return request

    # ========== PEER REVIEW ==========
    
    async def create_peer_review(self, review_data: PeerReview) -> PeerReview:
        """Create peer review of assignment"""
        assign_id = review_data.assignment_id
        self.peer_reviews[assign_id].append(review_data)
        return review_data

    async def get_peer_reviews(self, assignment_id: str) -> List[PeerReview]:
        """Get all reviews for an assignment"""
        return self.peer_reviews.get(assignment_id, [])

    async def get_peer_reviews_by_reviewer(self, reviewer_id: str) -> List[PeerReview]:
        """Get all reviews given by a user"""
        all_reviews = []
        for reviews in self.peer_reviews.values():
            all_reviews.extend([r for r in reviews if r.reviewer_id == reviewer_id])
        return all_reviews

    async def get_average_review_rating(self, assignment_id: str) -> float:
        """Get average rating for assignment"""
        reviews = self.peer_reviews.get(assignment_id, [])
        if not reviews:
            return 0.0
        return sum(r.rating for r in reviews) / len(reviews)

    # ========== STUDY SESSIONS ==========
    
    async def create_study_session(self, session_data: StudySession) -> StudySession:
        """Create live study session"""
        self.study_sessions[session_data.id] = session_data
        return session_data

    async def get_study_session(self, session_id: str) -> Optional[StudySession]:
        """Get study session"""
        return self.study_sessions.get(session_id)

    async def join_study_session(self, session_id: str, user_id: str) -> StudySession:
        """Join a study session"""
        if session_id not in self.study_sessions:
            raise ValueError("Session not found")
        
        session = self.study_sessions[session_id]
        
        if len(session.participants) >= session.max_participants:
            raise ValueError("Session is full")
        
        if user_id not in session.participants:
            session.participants.append(user_id)
        
        return session

    async def leave_study_session(self, session_id: str, user_id: str) -> bool:
        """Leave study session"""
        if session_id not in self.study_sessions:
            return False
        
        session = self.study_sessions[session_id]
        session.participants = [p for p in session.participants if p != user_id]
        return True

    async def get_upcoming_sessions(self, group_id: str, limit: int = 10) -> List[StudySession]:
        """Get upcoming study sessions for a group"""
        sessions = [s for s in self.study_sessions.values() if s.group_id == group_id and s.status == "scheduled"]
        return sorted(sessions, key=lambda s: s.scheduled_at)[:limit]

    # ========== RESOURCE SHARING ==========
    
    async def share_resource(self, resource_data: ResourceShare) -> ResourceShare:
        """Share learning resource"""
        self.resource_shares[resource_data.id] = resource_data
        return resource_data

    async def get_resource(self, resource_id: str) -> Optional[ResourceShare]:
        """Get resource"""
        return self.resource_shares.get(resource_id)

    async def get_group_resources(self, group_id: str) -> List[ResourceShare]:
        """Get resources shared in a group"""
        return [r for r in self.resource_shares.values() if r.group_id == group_id]

    async def increment_resource_downloads(self, resource_id: str) -> int:
        """Increment download count"""
        if resource_id in self.resource_shares:
            self.resource_shares[resource_id].downloads += 1
            return self.resource_shares[resource_id].downloads
        return 0

    # ========== ACHIEVEMENTS ==========
    
    async def award_achievement(self, user_id: str, badge_type: str, badge_name: str, description: str, points: int = 10) -> Achievement:
        """Award achievement badge to user"""
        achievement = Achievement(
            user_id=user_id,
            badge_type=badge_type,
            badge_name=badge_name,
            description=description,
            icon_url=f"/badges/{badge_type}.png",
            points_awarded=points
        )
        self.achievements[user_id].append(achievement)
        return achievement

    async def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Get all achievements for a user"""
        return self.achievements.get(user_id, [])

    async def get_total_points(self, user_id: str) -> int:
        """Get total points earned"""
        achievements = self.achievements.get(user_id, [])
        return sum(a.points_awarded for a in achievements)

    # ========== USER PROFILES ==========
    
    async def create_user_profile(self, profile_data: UserProfile) -> UserProfile:
        """Create user profile for peer learning"""
        self.user_profiles[profile_data.user_id] = profile_data
        return profile_data

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.user_profiles.get(user_id)

    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> UserProfile:
        """Update user profile"""
        if user_id not in self.user_profiles:
            raise ValueError("User profile not found")
        
        profile = self.user_profiles[user_id]
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        return profile

    async def find_mentors(self, topic: str, limit: int = 10) -> List[UserProfile]:
        """Find mentors by topic expertise"""
        potential_mentors = [
            p for p in self.user_profiles.values() 
            if topic in p.expertise and p.mentor_of_count < 5  # Not overloaded
        ]
        return sorted(potential_mentors, key=lambda p: p.reputation_score, reverse=True)[:limit]

    async def find_study_partners(self, user_id: str, subject: str, limit: int = 10) -> List[UserProfile]:
        """Find study partners with similar interests"""
        user = self.user_profiles.get(user_id)
        if not user:
            return []
        
        partners = [
            p for p in self.user_profiles.values() 
            if p.user_id != user_id and subject in p.learning_interests
        ]
        return sorted(partners, key=lambda p: p.reputation_score, reverse=True)[:limit]

    async def update_reputation_score(self, user_id: str, points: int) -> int:
        """Update user reputation score"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].reputation_score += points
            return self.user_profiles[user_id].reputation_score
        return 0

    # ========== ANALYTICS ==========
    
    async def get_study_group_analytics(self, group_id: str) -> Dict[str, Any]:
        """Get analytics for study group"""
        members = self.group_members.get(group_id, [])
        threads = [t for t in self.discussion_threads.values() if t.group_id == group_id]
        sessions = [s for s in self.study_sessions.values() if s.group_id == group_id]
        
        total_posts = sum(len(self.discussion_posts.get(t.id, [])) for t in threads)
        
        return {
            "group_id": group_id,
            "total_members": len(members),
            "active_members": len([m for m in members if m.is_active]),
            "total_discussions": len(threads),
            "total_posts": total_posts,
            "avg_posts_per_thread": total_posts / len(threads) if threads else 0,
            "total_sessions": len(sessions),
            "upcoming_sessions": len([s for s in sessions if s.status == "scheduled"]),
            "completed_sessions": len([s for s in sessions if s.status == "completed"])
        }

    async def get_user_collaboration_stats(self, user_id: str) -> Dict[str, Any]:
        """Get collaboration statistics for user"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {}
        
        # Count contributions
        posts = sum(len(posts) for posts in self.discussion_posts.values() 
                   for p in posts if p.creator_id == user_id)
        
        reviews = []
        for rev_list in self.peer_reviews.values():
            reviews.extend([r for r in rev_list if r.reviewer_id == user_id])
        
        mentorships = [r for r in self.mentorship_requests.values() if r.mentor_id == user_id]
        
        return {
            "user_id": user_id,
            "name": profile.name,
            "reputation_score": profile.reputation_score,
            "total_posts": posts,
            "total_reviews_given": len(reviews),
            "total_mentorships": len([m for m in mentorships if m.status == MentorshipStatus.ACTIVE]),
            "study_groups": profile.study_groups_count,
            "achievements": len(self.achievements.get(user_id, [])),
            "total_points": await self.get_total_points(user_id),
            "response_time_avg": profile.response_time_avg
        }
