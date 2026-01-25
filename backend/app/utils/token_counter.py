import tiktoken
from typing import List, Dict
from collections import defaultdict
from datetime import datetime, timedelta
from app.models.schema import Message

class TokenCounter:
    """
    Token counter for LLM API calls.
    - Tracks input tokens per user per day
    - Limit: 5k-10k tokens per day (using 10k as threshold warning)
    """
    
    def __init__(self, daily_token_limit: int = 10000):
        self.daily_token_limit = daily_token_limit
        self.user_tokens = defaultdict(dict)  # user_id -> {date: token_count}
        
        # Use cl100k_base encoding (used by GPT-3.5, GPT-4, and compatible with Groq)
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        try:
            tokens = self.encoder.encode(text)
            return len(tokens)
        except Exception as e:
            print(f"Token counting error: {e}")
            # Fallback: rough estimate (1 token ≈ 4 chars)
            return len(text) // 4
    
    def estimate_messages_tokens(self, messages: List[Message]) -> int:
        """Estimate tokens for a list of messages."""
        total = 0
        for msg in messages:
            # Each message has overhead: sender name + message content + formatting
            total += self.count_tokens(f"{msg.sender}: {msg.message}")
        return total
    
    def record_tokens(self, user_id: str, token_count: int) -> None:
        """Record token usage for the user on current date."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.user_tokens[user_id]:
            self.user_tokens[user_id][today] = 0
        self.user_tokens[user_id][today] += token_count
    
    def get_today_usage(self, user_id: str) -> Dict:
        """Get token usage for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        tokens_used = self.user_tokens[user_id].get(today, 0)
        
        return {
            "tokens_used_today": tokens_used,
            "daily_limit": self.daily_token_limit,
            "remaining_tokens": max(0, self.daily_token_limit - tokens_used),
            "percentage_used": round((tokens_used / self.daily_token_limit) * 100, 1),
            "date": today
        }
    
    def can_process(self, user_id: str, estimated_tokens: int) -> tuple[bool, str]:
        """
        Check if user can process more tokens.
        Returns: (allowed: bool, message: str)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        tokens_used = self.user_tokens[user_id].get(today, 0)
        tokens_after = tokens_used + estimated_tokens
        
        if tokens_after > self.daily_token_limit:
            remaining = self.daily_token_limit - tokens_used
            return False, f"Token limit exceeded. Used {tokens_used}/{self.daily_token_limit}. This request needs ~{estimated_tokens} tokens, but only {remaining} available. Resets tomorrow."
        
        # Warn if approaching limit (85%)
        if tokens_after > (self.daily_token_limit * 0.85):
            return True, f"⚠️ Warning: Approaching daily token limit. Used {tokens_after}/{self.daily_token_limit}."
        
        return True, "OK"
    
    def cleanup_old_records(self, days_to_keep: int = 7) -> None:
        """Clean up token records older than specified days."""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
        
        for user_id in list(self.user_tokens.keys()):
            dates_to_remove = [d for d in self.user_tokens[user_id].keys() if d < cutoff_date]
            for date in dates_to_remove:
                del self.user_tokens[user_id][date]
