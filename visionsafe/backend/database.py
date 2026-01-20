"""
Database operations: CSV read/write for violation logs.
Handles persistent storage of safety database.
"""

import pandas as pd
import os
from datetime import datetime
from typing import Optional, Dict, List


DATABASE_FILE = "safety_database.csv"


def record_violation(worker_id: int, missing_items: List[str], 
                    strikes: int, evidence_path: Optional[str] = None) -> Dict:
    """
    Create a violation record.
    
    Args:
        worker_id: Worker ID
        missing_items: List of missing PPE items
        strikes: Current strike count
        evidence_path: Path to evidence image
        
    Returns:
        Violation record dictionary
    """
    return {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ID": f"Worker-{worker_id}",
        "Violation": ", ".join(missing_items),
        "Strikes": strikes,
        "Evidence": evidence_path if evidence_path else ""
    }


def save_violation(violation_record: Dict) -> None:
    """
    Save violation record to CSV database.
    
    Args:
        violation_record: Violation record dictionary
    """
    try:
        df_new = pd.DataFrame([violation_record])
        
        if os.path.isfile(DATABASE_FILE):
            df_existing = pd.read_csv(DATABASE_FILE)
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
            # Keep only last 500 records
            df_final = df_final.tail(500)
        else:
            df_final = df_new
        
        df_final.to_csv(DATABASE_FILE, index=False)
    except Exception as e:
        print(f"Error saving violation: {e}")


def load_database() -> pd.DataFrame:
    """Load violation database."""
    try:
        if os.path.isfile(DATABASE_FILE):
            return pd.read_csv(DATABASE_FILE)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading database: {e}")
        return pd.DataFrame()


def get_statistics() -> Dict:
    """Get database statistics."""
    df = load_database()
    
    if df.empty:
        return {
            "total_violations": 0,
            "unique_workers": 0,
            "most_common_violation": "None"
        }
    
    stats = {
        "total_violations": len(df),
        "unique_workers": df['ID'].nunique(),
        "most_common_violation": df['Violation'].mode()[0] if not df.empty else "None"
    }
    
    return stats


def clear_database() -> None:
    """Clear all database records."""
    try:
        if os.path.isfile(DATABASE_FILE):
            os.remove(DATABASE_FILE)
    except Exception as e:
        print(f"Error clearing database: {e}")


def export_csv(filepath: str = "safety_export.csv") -> str:
    """Export database to CSV file."""
    try:
        df = load_database()
        df.to_csv(filepath, index=False)
        return filepath
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return None


def get_violations_by_hour() -> Dict:
    """Get violation counts by hour."""
    df = load_database()
    if df.empty:
        return {}
    
    df['Hour'] = pd.to_datetime(df['Time']).dt.hour
    return df['Hour'].value_counts().sort_index().to_dict()


def get_violations_by_type() -> Dict:
    """Get violation counts by type."""
    df = load_database()
    if df.empty:
        return {}
    
    all_violations = []
    for v in df['Violation']:
        all_violations.extend(v.split(", "))
    
    return pd.Series(all_violations).value_counts().to_dict()
