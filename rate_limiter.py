from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, limit: int = 5, window: int = 60):
        """
        Initialize rate limiter
        :param limit: Maximum number of requests allowed in the time window
        :param window: Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.user_requests = defaultdict(list)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if user is allowed to make a request
        :param user_id: Telegram user ID
        :return: True if request is allowed, False otherwise
        """
        now = datetime.now()
        user_times = self.user_requests[user_id]

        # Remove old requests
        user_times = [time for time in user_times if now - time < timedelta(seconds=self.window)]
        self.user_requests[user_id] = user_times

        # Check if user has exceeded limit
        if len(user_times) >= self.limit:
            return False

        # Add new request
        user_times.append(now)
        return True

    def get_remaining_time(self, user_id: int) -> int:
        """
        Get remaining time until next request is allowed
        :param user_id: Telegram user ID
        :return: Time in seconds until next request is allowed, 0 if requests are allowed
        """
        if len(self.user_requests[user_id]) < self.limit:
            return 0

        now = datetime.now()
        oldest_request = min(self.user_requests[user_id])
        time_passed = (now - oldest_request).total_seconds()

        return max(0, int(self.window - time_passed))
