"""
PPE violation tracking: Strike system and cooldown logic.
Handles worker violation history and strike counting.
"""

import time
from typing import Dict, List


def update_strikes(worker: Dict, missing_items: List[str], cooldown: float = 5.0) -> bool:
    """
    Update worker strike count with cooldown and violation tracking.
    
    Args:
        worker: Worker record dict with 'strikes', 'last_violation', 'last_strike_time'
        missing_items: List of missing PPE items
        cooldown: Cooldown period in seconds
        
    Returns:
        True if a new strike was recorded, False otherwise
    """
    now = time.time()
    
    # Create signature from sorted missing items to detect new violations
    current_signature = sorted(missing_items)
    last_signature = worker.get('last_violation', [])
    
    # Check conditions: has missing items, new violation type, cooldown expired
    is_new_violation = current_signature != last_signature
    cooldown_expired = (now - worker.get('last_strike_time', 0)) > cooldown
    has_violations = len(missing_items) > 0
    
    if has_violations and is_new_violation and cooldown_expired:
        worker['strikes'] += 1
        worker['last_violation'] = current_signature
        worker['last_strike_time'] = now
        return True
    
    # Reset last violation if now safe
    if not has_violations:
        worker['last_violation'] = []
    
    return False


def is_fired(strikes: int, max_strikes: int = 15) -> bool:
    """Check if worker exceeds strike limit."""
    return strikes >= max_strikes


def reset_worker(worker: Dict) -> None:
    """Reset worker strikes and history."""
    worker['strikes'] = 0
    worker['last_violation'] = []
    worker['last_strike_time'] = 0


def get_worker_status(worker: Dict, missing_items: List[str], max_strikes: int = 15) -> tuple:
    """
    Get worker status information.
    
    Returns:
        (status_color, status_label, is_fired)
    """
    strikes = worker.get('strikes', 0)
    
    if strikes >= max_strikes:
        return (0, 0, 255), "FIRED!", True
    elif len(missing_items) > 0:
        return (0, 165, 255), "UNSAFE", False
    else:
        return (0, 255, 0), "SAFE", False
