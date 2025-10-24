"""
Lightweight logging system
"""

import os
from datetime import datetime
from typing import Optional


class RunLogger:
    """Logs run statistics to out/run.log"""
    
    def __init__(self, log_path: str = 'out/run.log'):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    def log_run(
        self,
        symbols_count: int,
        changes_count: int,
        runtime_seconds: float,
        error: Optional[str] = None
    ):
        """
        Log a completed run
        
        Args:
            symbols_count: Number of symbols processed
            changes_count: Number of regime changes detected
            runtime_seconds: Total runtime in seconds
            error: Optional error message if run failed
        """
        timestamp = datetime.now().isoformat()
        
        if error:
            entry = (
                f"[{timestamp}] ERROR: {error}\n"
            )
        else:
            entry = (
                f"[{timestamp}] "
                f"Symbols: {symbols_count}, "
                f"Changes: {changes_count}, "
                f"Runtime: {runtime_seconds:.2f}s\n"
            )
        
        with open(self.log_path, 'a') as f:
            f.write(entry)
    
    def get_recent_logs(self, lines: int = 10) -> str:
        """Get recent log entries"""
        if not os.path.exists(self.log_path):
            return "No logs yet"
        
        with open(self.log_path, 'r') as f:
            all_lines = f.readlines()
        
        recent = all_lines[-lines:]
        return ''.join(recent)
