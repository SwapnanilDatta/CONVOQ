import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Tuple

class RateLimiter:
    """
    Per-user rate limiter with minute and daily limits.
    - Max 3 requests per minute
    - Max 30-50 requests per day (using 50 for threshold warning)
    """
    
    def __init__(self, requests_per_minute: int = 3, requests_per_day: int = 50):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        
        # Store timestamps of requests per user
        self.user_requests = defaultdict(list)  # user_id -> list of timestamps
        
    def is_allowed(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user is allowed to make a request.
        Returns: (allowed: bool, message: str)
        """
        now = time.time()
        current_time = datetime.now()
        
        # Get user's request history
        requests = self.user_requests[user_id]
        
        # Remove requests older than 24 hours
        day_ago = (current_time - timedelta(days=1)).timestamp()
        requests[:] = [ts for ts in requests if ts > day_ago]
        
        # Check daily limit
        if len(requests) >= self.requests_per_day:
            return False, f"Daily limit reached ({self.requests_per_day} requests/day). Try again tomorrow."
        
        # Check minute limit (requests in last 60 seconds)
        minute_ago = now - 60
        recent_requests = [ts for ts in requests if ts > minute_ago]
        
        if len(recent_requests) >= self.requests_per_minute:
            retry_after = int(recent_requests[0] + 60 - now) + 1
            return False, f"Rate limited: 3 requests per minute. Retry in {retry_after}s."
        
        return True, "OK"
    
    def record_request(self, user_id: str) -> None:
        """Record a new request for the user."""
        self.user_requests[user_id].append(time.time())
    
    def get_usage(self, user_id: str) -> dict:
        """Get current usage stats for user."""
        now = time.time()
        current_time = datetime.now()
        
        requests = self.user_requests[user_id]
        
        # Remove old requests
        day_ago = (current_time - timedelta(days=1)).timestamp()
        requests[:] = [ts for ts in requests if ts > day_ago]
        
        minute_ago = now - 60
        recent_requests = [ts for ts in requests if ts > minute_ago]
        
        return {
            "requests_this_minute": len(recent_requests),
            "requests_today": len(requests),
            "daily_limit": self.requests_per_day,
            "minute_limit": self.requests_per_minute,
            "remaining_today": self.requests_per_day - len(requests)
        }
