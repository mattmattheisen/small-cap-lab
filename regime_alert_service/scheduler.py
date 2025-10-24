"""
Scheduler with trading day checks and duplicate run prevention
"""

import os
from datetime import datetime
from typing import Optional
import pytz


class Scheduler:
    """Handles run timing and Sunday skip logic"""
    
    def __init__(self, timezone: str = 'America/Chicago'):
        self.timezone = pytz.timezone(timezone)
        self.last_run_file = 'data/last_run.txt'
    
    def should_run(self) -> tuple[bool, Optional[str]]:
        """
        Check if service should run now
        
        Returns:
            Tuple of (should_run: bool, reason: str or None)
        """
        now = datetime.now(self.timezone)
        
        # Check if Sunday
        if now.weekday() == 6:  # Sunday
            return False, "Sunday - skipping"
        
        # Check if already ran today
        today_str = now.strftime('%Y-%m-%d')
        if self._already_ran_today(today_str):
            return False, f"Already ran today ({today_str})"
        
        return True, None
    
    def _already_ran_today(self, today_str: str) -> bool:
        """Check if service already ran today"""
        if not os.path.exists(self.last_run_file):
            return False
        
        with open(self.last_run_file, 'r') as f:
            last_run = f.read().strip()
        
        return last_run == today_str
    
    def mark_run_complete(self):
        """Record that service ran today"""
        os.makedirs(os.path.dirname(self.last_run_file), exist_ok=True)
        now = datetime.now(self.timezone)
        today_str = now.strftime('%Y-%m-%d')
        
        with open(self.last_run_file, 'w') as f:
            f.write(today_str)
    
    def get_scheduled_times(self) -> list[str]:
        """Return configured run times"""
        return ['08:05', '15:10']
    
    def is_scheduled_time(self, window_minutes: int = 5) -> bool:
        """
        Check if current time is within a scheduled run window
        
        Args:
            window_minutes: Minutes before/after scheduled time to allow
        """
        now = datetime.now(self.timezone)
        current_time = now.strftime('%H:%M')
        
        scheduled_times = self.get_scheduled_times()
        
        for scheduled_time in scheduled_times:
            # Parse scheduled time
            hour, minute = map(int, scheduled_time.split(':'))
            scheduled_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Check if within window
            diff_minutes = abs((now - scheduled_dt).total_seconds() / 60)
            if diff_minutes <= window_minutes:
                return True
        
        return False
