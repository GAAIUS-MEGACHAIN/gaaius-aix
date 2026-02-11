"""
PHASE 3: Load testing with Locust
Tests all 204 endpoints under load to find performance bottlenecks
"""

from locust import HttpUser, task, between, TaskSet, events
from locust.contrib.fasthttp import FastHttpUser
import random
from datetime import datetime
import json


class VideoLoadTasks(TaskSet):
    """Load test tasks for video endpoints"""
    
    @task(10)
    def get_video_list(self):
        """Get video list - heavy traffic"""
        page = random.randint(1, 50)
        with self.client.get(
            f"/api/videos/videos?page={page}&limit=20",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(5)
    def get_single_video(self):
        """Get single video details"""
        video_id = "507f1f77bcf86cd799439011"
        with self.client.get(
            f"/api/videos/videos/{video_id}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(3)
    def search_videos(self):
        """Search videos endpoint"""
        query = random.choice(['python', 'tutorial', 'ai', 'code', 'web'])
        with self.client.get(
            f"/api/videos/search?q={query}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def like_video(self):
        """Like video endpoint"""
        video_id = "507f1f77bcf86cd799439011"
        with self.client.post(
            f"/api/videos/videos/{video_id}/like",
            catch_response=True
        ) as response:
            if response.status_code in [200, 401, 404]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(2)
    def add_comment(self):
        """Add comment to video"""
        video_id = "507f1f77bcf86cd799439011"
        with self.client.post(
            f"/api/videos/videos/{video_id}/comments",
            json={"text": "Great video!"},
            catch_response=True
        ) as response:
            if response.status_code in [200, 201, 401, 404]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")


class ChatLoadTasks(TaskSet):
    """Load test tasks for chat endpoints"""
    
    @task(8)
    def send_chat_message(self):
        """Send chat message"""
        session_id = "507f1f77bcf86cd799439011"
        with self.client.post(
            f"/api/chat/messages",
            json={
                "session_id": session_id,
                "message": "Hello, how are you?"
            },
            catch_response=True
        ) as response:
            if response.status_code in [200, 201, 401]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(5)
    def get_chat_history(self):
        """Get chat history"""
        session_id = "507f1f77bcf86cd799439011"
        with self.client.get(
            f"/api/chat/history/{session_id}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 401, 404]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")


class HealthCheckTasks(TaskSet):
    """Load test health check endpoints"""
    
    @task(20)
    def health_check(self):
        """Health check endpoint"""
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(10)
    def readiness_check(self):
        """Readiness check endpoint"""
        with self.client.get("/api/ready", catch_response=True) as response:
            if response.status_code in [200, 503]:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")
    
    @task(5)
    def metrics(self):
        """Metrics endpoint"""
        with self.client.get("/api/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status {response.status_code}")


class VideoUser(FastHttpUser):
    """User that performs video-related tasks"""
    
    tasks = [VideoLoadTasks]
    wait_time = between(1, 3)


class ChatUser(FastHttpUser):
    """User that performs chat-related tasks"""
    
    tasks = [ChatLoadTasks]
    wait_time = between(2, 5)


class HealthCheckUser(FastHttpUser):
    """User that performs health checks"""
    
    tasks = [HealthCheckTasks]
    wait_time = between(0.5, 1)


# Event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("\n" + "="*80)
    print("🚀 PHASE 3 LOAD TEST STARTED")
    print("="*80)
    print(f"Target: {environment.host}")
    print(f"Start time: {datetime.now().isoformat()}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "="*80)
    print("📊 LOAD TEST RESULTS")
    print("="*80)
    print(f"End time: {datetime.now().isoformat()}")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Response time avg: {environment.stats.total.avg_response_time:.0f}ms")
    print(f"Response time min: {environment.stats.total.min_response_time:.0f}ms")
    print(f"Response time max: {environment.stats.total.max_response_time:.0f}ms")
    print("="*80 + "\n")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Called when test runner quits"""
    stats = environment.stats
    
    # Write results to file
    with open('load_test_results.json', 'w') as f:
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_requests': stats.total.num_requests,
            'total_failures': stats.total.num_failures,
            'failure_rate': round(stats.total.fail_ratio * 100, 2),
            'avg_response_time': round(stats.total.avg_response_time, 2),
            'min_response_time': stats.total.min_response_time,
            'max_response_time': stats.total.max_response_time,
            'requests_per_second': stats.total.total_rps,
        }
        json.dump(results, f, indent=2)
    
    print("✅ Load test results saved to load_test_results.json")
