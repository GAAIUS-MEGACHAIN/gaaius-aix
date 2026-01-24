"""
Peer Learning & Collaboration Routes
REST API endpoints for study groups, mentorship, discussions, and collaboration
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from peer_learning_service import (
    PeerLearningService,
    StudyGroupMetadata,
    StudyGroupMember,
    ParticipantRole,
    DiscussionThread,
    DiscussionPost,
    DiscussionCategory,
    PostType,
    MentorshipRequest,
    MentorshipStatus,
    MentorshipSession,
    PeerReview,
    StudySession,
    ResourceShare,
    UserProfile,
    Achievement,
    CollaborationStatus
)

# ============================================================================
# SERVICE INITIALIZATION
# ============================================================================

router = APIRouter(prefix="/peer-learning", tags=["peer-learning"])
peer_learning_service = PeerLearningService()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_service() -> PeerLearningService:
    """Get peer learning service instance"""
    return peer_learning_service

# ============================================================================
# STUDY GROUP ENDPOINTS
# ============================================================================

@router.post("/study-groups/create")
async def create_study_group(
    name: str = Body(...),
    description: str = Body(...),
    course_id: str = Body(...),
    subject: str = Body(...),
    level: str = Body(...),
    creator_id: str = Body(...),
    max_members: int = Body(default=10),
    goals: List[str] = Body(default_factory=list),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create a new study group"""
    try:
        group = StudyGroupMetadata(
            name=name,
            description=description,
            course_id=course_id,
            subject=subject,
            level=level,
            max_members=max_members,
            goals=goals,
            creator_id=creator_id
        )
        
        created_group = await service.create_study_group(group)
        
        return {
            "status": "success",
            "group": created_group.dict(),
            "message": f"Study group '{name}' created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/study-groups/{group_id}")
async def get_study_group(
    group_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get study group details"""
    group = await service.get_study_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Study group not found")
    
    members = await service.get_group_members(group_id)
    analytics = await service.get_study_group_analytics(group_id)
    
    return {
        "status": "success",
        "group": group.dict(),
        "members_count": len(members),
        "analytics": analytics
    }

@router.get("/study-groups")
async def list_study_groups(
    course_id: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """List study groups with optional filters"""
    groups = await service.list_study_groups(course_id=course_id, subject=subject)
    
    return {
        "status": "success",
        "groups": [g.dict() for g in groups],
        "total": len(groups)
    }

@router.put("/study-groups/{group_id}")
async def update_study_group(
    group_id: str,
    updates: Dict[str, Any] = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Update study group"""
    try:
        updated_group = await service.update_study_group(group_id, updates)
        return {
            "status": "success",
            "group": updated_group.dict(),
            "message": "Study group updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/study-groups/{group_id}/members/add")
async def add_member_to_group(
    group_id: str,
    user_id: str = Body(...),
    role: str = Body(default="member"),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Add member to study group"""
    try:
        member = await service.add_member_to_group(
            group_id, 
            user_id, 
            ParticipantRole(role)
        )
        return {
            "status": "success",
            "member": member.dict(),
            "message": "Member added to study group"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/study-groups/{group_id}/members/remove")
async def remove_member_from_group(
    group_id: str,
    user_id: str = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Remove member from study group"""
    removed = await service.remove_member_from_group(group_id, user_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Member or group not found")
    
    return {
        "status": "success",
        "message": "Member removed from study group"
    }

@router.get("/study-groups/{group_id}/members")
async def get_group_members(
    group_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all members in study group"""
    members = await service.get_group_members(group_id)
    
    return {
        "status": "success",
        "members": [m.dict() for m in members],
        "total": len(members)
    }

@router.put("/study-groups/{group_id}/members/{user_id}/role")
async def update_member_role(
    group_id: str,
    user_id: str,
    new_role: str = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Update member role in group"""
    try:
        member = await service.update_member_role(
            group_id, 
            user_id, 
            ParticipantRole(new_role)
        )
        return {
            "status": "success",
            "member": member.dict(),
            "message": f"Member role updated to {new_role}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ============================================================================
# DISCUSSION FORUM ENDPOINTS
# ============================================================================

@router.post("/discussions/thread/create")
async def create_discussion_thread(
    title: str = Body(...),
    description: str = Body(default=""),
    creator_id: str = Body(...),
    category: str = Body(...),
    group_id: Optional[str] = Body(None),
    course_id: Optional[str] = Body(None),
    tags: List[str] = Body(default_factory=list),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create discussion thread"""
    try:
        thread = DiscussionThread(
            title=title,
            description=description,
            creator_id=creator_id,
            category=DiscussionCategory(category),
            group_id=group_id,
            course_id=course_id,
            tags=tags
        )
        
        created_thread = await service.create_discussion_thread(thread)
        
        return {
            "status": "success",
            "thread": created_thread.dict(),
            "message": "Discussion thread created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/discussions/thread/{thread_id}/post")
async def create_discussion_post(
    thread_id: str,
    content: str = Body(...),
    creator_id: str = Body(...),
    post_type: str = Body(default="discussion"),
    attachments: List[Dict[str, str]] = Body(default_factory=list),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create discussion post"""
    try:
        post = DiscussionPost(
            thread_id=thread_id,
            content=content,
            creator_id=creator_id,
            post_type=PostType(post_type),
            attachments=attachments
        )
        
        created_post = await service.create_discussion_post(post)
        
        return {
            "status": "success",
            "post": created_post.dict(),
            "message": "Discussion post created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/discussions/thread/{thread_id}")
async def get_discussion_thread(
    thread_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get discussion thread details"""
    thread = await service.get_discussion_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    posts = await service.get_discussion_posts(thread_id)
    
    return {
        "status": "success",
        "thread": thread.dict(),
        "posts": [p.dict() for p in posts],
        "posts_count": len(posts)
    }

@router.get("/discussions/thread/{thread_id}/posts")
async def get_discussion_posts(
    thread_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all posts in thread"""
    posts = await service.get_discussion_posts(thread_id)
    
    return {
        "status": "success",
        "posts": [p.dict() for p in posts],
        "total": len(posts)
    }

@router.get("/discussions/threads")
async def list_discussion_threads(
    group_id: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """List discussion threads"""
    threads = await service.list_discussion_threads(group_id=group_id, course_id=course_id)
    
    return {
        "status": "success",
        "threads": [t.dict() for t in threads],
        "total": len(threads)
    }

@router.post("/discussions/post/{post_id}/vote")
async def vote_on_post(
    thread_id: str,
    post_id: str,
    vote: int = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Vote on discussion post"""
    try:
        if vote not in [-1, 1]:
            raise ValueError("Vote must be 1 or -1")
        
        votes = await service.vote_on_post(post_id, thread_id, vote)
        
        return {
            "status": "success",
            "votes": votes,
            "message": "Vote recorded"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/discussions/thread/{thread_id}/post/{post_id}/mark-answer")
async def mark_as_answer(
    thread_id: str,
    post_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Mark post as accepted answer"""
    success = await service.mark_post_as_answer(thread_id, post_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "status": "success",
        "message": "Post marked as accepted answer"
    }

# ============================================================================
# MENTORSHIP ENDPOINTS
# ============================================================================

@router.post("/mentorship/request/create")
async def create_mentorship_request(
    mentee_id: str = Body(...),
    mentor_id: str = Body(...),
    topic: str = Body(...),
    goals: str = Body(...),
    duration_weeks: int = Body(...),
    frequency: str = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create mentorship request"""
    try:
        request = MentorshipRequest(
            mentee_id=mentee_id,
            mentor_id=mentor_id,
            topic=topic,
            goals=goals,
            duration_weeks=duration_weeks,
            frequency=frequency
        )
        
        created_request = await service.create_mentorship_request(request)
        
        return {
            "status": "success",
            "request": created_request.dict(),
            "message": "Mentorship request created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/mentorship/request/{request_id}")
async def get_mentorship_request(
    request_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get mentorship request"""
    request = await service.get_mentorship_request(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    sessions = await service.get_mentorship_sessions(request_id)
    
    return {
        "status": "success",
        "request": request.dict(),
        "sessions": [s.dict() for s in sessions],
        "sessions_count": len(sessions)
    }

@router.post("/mentorship/request/{request_id}/accept")
async def accept_mentorship_request(
    request_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Accept mentorship request"""
    try:
        accepted_request = await service.accept_mentorship_request(request_id)
        
        return {
            "status": "success",
            "request": accepted_request.dict(),
            "message": "Mentorship request accepted"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/mentorship/request/{request_id}/decline")
async def decline_mentorship_request(
    request_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Decline mentorship request"""
    try:
        declined_request = await service.decline_mentorship_request(request_id)
        
        return {
            "status": "success",
            "request": declined_request.dict(),
            "message": "Mentorship request declined"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/mentorship/session/schedule")
async def schedule_mentorship_session(
    mentorship_request_id: str = Body(...),
    mentor_id: str = Body(...),
    mentee_id: str = Body(...),
    scheduled_at: datetime = Body(...),
    topic: str = Body(...),
    duration_minutes: int = Body(default=60),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Schedule mentorship session"""
    try:
        session = MentorshipSession(
            mentorship_request_id=mentorship_request_id,
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            scheduled_at=scheduled_at,
            topic=topic,
            duration_minutes=duration_minutes
        )
        
        created_session = await service.schedule_mentorship_session(session)
        
        return {
            "status": "success",
            "session": created_session.dict(),
            "message": "Mentorship session scheduled"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/mentorship/{request_id}/sessions")
async def get_mentorship_sessions(
    request_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all sessions for mentorship"""
    sessions = await service.get_mentorship_sessions(request_id)
    
    return {
        "status": "success",
        "sessions": [s.dict() for s in sessions],
        "total": len(sessions)
    }

@router.post("/mentorship/request/{request_id}/complete")
async def complete_mentorship(
    request_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Mark mentorship as completed"""
    try:
        completed = await service.complete_mentorship(request_id)
        
        return {
            "status": "success",
            "request": completed.dict(),
            "message": "Mentorship marked as completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/mentorship/mentors")
async def find_mentors(
    topic: str = Query(...),
    limit: int = Query(default=10),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Find mentors by topic"""
    mentors = await service.find_mentors(topic, limit=limit)
    
    return {
        "status": "success",
        "mentors": [m.dict() for m in mentors],
        "total": len(mentors)
    }

@router.get("/mentorship/study-partners")
async def find_study_partners(
    user_id: str = Query(...),
    subject: str = Query(...),
    limit: int = Query(default=10),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Find study partners with similar interests"""
    partners = await service.find_study_partners(user_id, subject, limit=limit)
    
    return {
        "status": "success",
        "partners": [p.dict() for p in partners],
        "total": len(partners)
    }

# ============================================================================
# PEER REVIEW ENDPOINTS
# ============================================================================

@router.post("/peer-review/create")
async def create_peer_review(
    assignment_id: str = Body(...),
    submitter_id: str = Body(...),
    reviewer_id: str = Body(...),
    rating: int = Body(...),
    feedback: str = Body(...),
    strengths: List[str] = Body(default_factory=list),
    improvements: List[str] = Body(default_factory=list),
    suggestions: List[str] = Body(default_factory=list),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create peer review"""
    try:
        review = PeerReview(
            assignment_id=assignment_id,
            submitter_id=submitter_id,
            reviewer_id=reviewer_id,
            rating=rating,
            feedback=feedback,
            strengths=strengths,
            improvements=improvements,
            suggestions=suggestions
        )
        
        created_review = await service.create_peer_review(review)
        
        return {
            "status": "success",
            "review": created_review.dict(),
            "message": "Peer review created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/peer-review/assignment/{assignment_id}")
async def get_peer_reviews(
    assignment_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all reviews for assignment"""
    reviews = await service.get_peer_reviews(assignment_id)
    avg_rating = await service.get_average_review_rating(assignment_id)
    
    return {
        "status": "success",
        "reviews": [r.dict() for r in reviews],
        "total": len(reviews),
        "average_rating": avg_rating
    }

@router.get("/peer-review/reviewer/{reviewer_id}")
async def get_reviews_by_reviewer(
    reviewer_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all reviews given by a reviewer"""
    reviews = await service.get_peer_reviews_by_reviewer(reviewer_id)
    
    return {
        "status": "success",
        "reviews": [r.dict() for r in reviews],
        "total": len(reviews)
    }

# ============================================================================
# STUDY SESSION ENDPOINTS
# ============================================================================

@router.post("/study-session/create")
async def create_study_session(
    group_id: str = Body(...),
    title: str = Body(...),
    topic: str = Body(...),
    creator_id: str = Body(...),
    scheduled_at: datetime = Body(...),
    duration_minutes: int = Body(default=90),
    max_participants: int = Body(default=15),
    agenda: List[str] = Body(default_factory=list),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create live study session"""
    try:
        session = StudySession(
            group_id=group_id,
            title=title,
            topic=topic,
            creator_id=creator_id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            max_participants=max_participants,
            agenda=agenda
        )
        
        created_session = await service.create_study_session(session)
        
        return {
            "status": "success",
            "session": created_session.dict(),
            "message": "Study session created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/study-session/{session_id}")
async def get_study_session(
    session_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get study session"""
    session = await service.get_study_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "status": "success",
        "session": session.dict()
    }

@router.post("/study-session/{session_id}/join")
async def join_study_session(
    session_id: str,
    user_id: str = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Join study session"""
    try:
        session = await service.join_study_session(session_id, user_id)
        
        return {
            "status": "success",
            "session": session.dict(),
            "message": "Joined study session",
            "participants_count": len(session.participants)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/study-session/{session_id}/leave")
async def leave_study_session(
    session_id: str,
    user_id: str = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Leave study session"""
    success = await service.leave_study_session(session_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session or user not found")
    
    return {
        "status": "success",
        "message": "Left study session"
    }

@router.get("/study-session/group/{group_id}/upcoming")
async def get_upcoming_sessions(
    group_id: str,
    limit: int = Query(default=10),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get upcoming study sessions"""
    sessions = await service.get_upcoming_sessions(group_id, limit=limit)
    
    return {
        "status": "success",
        "sessions": [s.dict() for s in sessions],
        "total": len(sessions)
    }

# ============================================================================
# RESOURCE SHARING ENDPOINTS
# ============================================================================

@router.post("/resource/share")
async def share_resource(
    user_id: str = Body(...),
    resource_type: str = Body(...),
    title: str = Body(...),
    description: str = Body(...),
    resource_url: str = Body(...),
    group_id: Optional[str] = Body(None),
    relevance_tags: List[str] = Body(default_factory=list),
    access_level: str = Body(default="public"),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Share learning resource"""
    try:
        resource = ResourceShare(
            user_id=user_id,
            resource_type=resource_type,
            title=title,
            description=description,
            resource_url=resource_url,
            group_id=group_id,
            relevance_tags=relevance_tags,
            access_level=access_level
        )
        
        shared_resource = await service.share_resource(resource)
        
        return {
            "status": "success",
            "resource": shared_resource.dict(),
            "message": "Resource shared successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/resource/{resource_id}")
async def get_resource(
    resource_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get resource details"""
    resource = await service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    await service.increment_resource_downloads(resource_id)
    
    return {
        "status": "success",
        "resource": resource.dict()
    }

@router.get("/resource/group/{group_id}/resources")
async def get_group_resources(
    group_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get resources shared in group"""
    resources = await service.get_group_resources(group_id)
    
    return {
        "status": "success",
        "resources": [r.dict() for r in resources],
        "total": len(resources)
    }

# ============================================================================
# ACHIEVEMENTS & BADGES ENDPOINTS
# ============================================================================

@router.post("/achievement/award")
async def award_achievement(
    user_id: str = Body(...),
    badge_type: str = Body(...),
    badge_name: str = Body(...),
    description: str = Body(...),
    points: int = Body(default=10),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Award achievement to user"""
    try:
        achievement = await service.award_achievement(
            user_id, badge_type, badge_name, description, points
        )
        
        return {
            "status": "success",
            "achievement": achievement.dict(),
            "message": "Achievement awarded"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/achievement/user/{user_id}")
async def get_user_achievements(
    user_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get all achievements for user"""
    achievements = await service.get_user_achievements(user_id)
    total_points = await service.get_total_points(user_id)
    
    return {
        "status": "success",
        "achievements": [a.dict() for a in achievements],
        "total": len(achievements),
        "total_points": total_points
    }

# ============================================================================
# USER PROFILE ENDPOINTS
# ============================================================================

@router.post("/profile/create")
async def create_user_profile(
    user_id: str = Body(...),
    name: str = Body(...),
    email: str = Body(...),
    bio: Optional[str] = Body(None),
    expertise: List[str] = Body(default_factory=list),
    learning_interests: List[str] = Body(default_factory=list),
    timezone: str = Body(default="UTC"),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Create user profile"""
    try:
        profile = UserProfile(
            user_id=user_id,
            name=name,
            email=email,
            bio=bio,
            expertise=expertise,
            learning_interests=learning_interests,
            timezone=timezone
        )
        
        created_profile = await service.create_user_profile(profile)
        
        return {
            "status": "success",
            "profile": created_profile.dict(),
            "message": "User profile created"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile/{user_id}")
async def get_user_profile(
    user_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get user profile"""
    profile = await service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    stats = await service.get_user_collaboration_stats(user_id)
    
    return {
        "status": "success",
        "profile": profile.dict(),
        "collaboration_stats": stats
    }

@router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: str,
    updates: Dict[str, Any] = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Update user profile"""
    try:
        updated_profile = await service.update_user_profile(user_id, updates)
        
        return {
            "status": "success",
            "profile": updated_profile.dict(),
            "message": "Profile updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/profile/{user_id}/reputation")
async def update_reputation(
    user_id: str,
    points: int = Body(...),
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Update user reputation score"""
    new_score = await service.update_reputation_score(user_id, points)
    
    return {
        "status": "success",
        "reputation_score": new_score,
        "message": f"Reputation updated by {points} points"
    }

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/study-group/{group_id}")
async def get_study_group_analytics(
    group_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get study group analytics"""
    analytics = await service.get_study_group_analytics(group_id)
    
    return {
        "status": "success",
        "analytics": analytics
    }

@router.get("/analytics/user/{user_id}")
async def get_user_collaboration_stats(
    user_id: str,
    service: PeerLearningService = Depends(get_service)
) -> Dict[str, Any]:
    """Get user collaboration statistics"""
    stats = await service.get_user_collaboration_stats(user_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "status": "success",
        "stats": stats
    }
