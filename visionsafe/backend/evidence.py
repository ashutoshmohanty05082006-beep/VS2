"""
Evidence management: Snapshot saving and handling.
Manages evidence image capture and file organization.
"""

import os
import cv2
from datetime import datetime
from typing import Optional


EVIDENCE_DIR = "evidence_snaps"


def ensure_evidence_dir() -> None:
    """Create evidence directory if it doesn't exist."""
    if not os.path.exists(EVIDENCE_DIR):
        os.makedirs(EVIDENCE_DIR)


def save_snapshot(frame, worker_id: int) -> Optional[str]:
    """
    Save evidence snapshot of violation.
    
    Args:
        frame: Frame to save
        worker_id: ID of worker
        
    Returns:
        Path to saved image, or None if save failed
    """
    try:
        ensure_evidence_dir()
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"{EVIDENCE_DIR}/Worker{worker_id}_{timestamp}.jpg"
        
        # Ensure unique filename
        counter = 1
        while os.path.exists(filename):
            filename = f"{EVIDENCE_DIR}/Worker{worker_id}_{timestamp}_{counter}.jpg"
            counter += 1
        
        cv2.imwrite(filename, frame)
        return filename
    except Exception as e:
        print(f"Error saving snapshot: {e}")
        return None


def get_evidence_file(filepath: str) -> Optional[bytes]:
    """Read evidence file as bytes for download."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return f.read()
        return None
    except Exception as e:
        print(f"Error reading evidence file: {e}")
        return None


def clear_evidence_dir() -> None:
    """Clear all evidence snapshots."""
    try:
        if os.path.exists(EVIDENCE_DIR):
            for file in os.listdir(EVIDENCE_DIR):
                filepath = os.path.join(EVIDENCE_DIR, file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
    except Exception as e:
        print(f"Error clearing evidence: {e}")


def get_evidence_files() -> list:
    """Get list of all evidence files."""
    ensure_evidence_dir()
    try:
        return [f for f in os.listdir(EVIDENCE_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    except:
        return []
