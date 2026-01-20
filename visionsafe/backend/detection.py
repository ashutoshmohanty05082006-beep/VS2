"""
Detection module: YOLO model loading and tracking.
Handles model initialization and frame-level detection.
"""

from ultralytics import YOLO
import streamlit as st
import numpy as np
import cv2


@st.cache_resource
def load_model(path: str) -> YOLO:
    """Load YOLO model with caching for performance."""
    return YOLO(path)


def run_detection(model: YOLO, frame: np.ndarray, conf: float = 0.4, persist: bool = True):
    """
    Run YOLO detection on a frame with tracking.
    
    Args:
        model: YOLO model instance
        frame: Input frame (BGR numpy array)
        conf: Confidence threshold
        persist: Enable tracking persistence across frames
        
    Returns:
        results: YOLO results object
    """
    results = model.track(frame, persist=persist, conf=conf, verbose=False)
    return results


def extract_detections(results) -> tuple:
    """
    Extract and categorize detections from YOLO results.
    
    Returns:
        (boxes, classes, track_ids, person_indices, ppe_indices)
    """
    if results[0].boxes.id is None:
        return None, None, None, [], []
    
    boxes = results[0].boxes.xyxy.cpu().numpy()
    classes = results[0].boxes.cls.cpu().numpy()
    track_ids = results[0].boxes.id.int().cpu().numpy()
    
    # Separate persons (class 0) from PPE (classes 1-6)
    person_indices = [i for i, cls in enumerate(classes) if cls == 0]
    ppe_indices = [i for i, cls in enumerate(classes) if cls != 0]
    
    return boxes, classes, track_ids, person_indices, ppe_indices


def draw_annotations(frame: np.ndarray, boxes, classes, track_ids, person_indices, 
                     colors: dict = None) -> np.ndarray:
    """
    Draw bounding boxes and labels on frame.
    
    Args:
        frame: Input frame
        boxes: Bounding boxes array
        classes: Class IDs array
        track_ids: Track IDs array
        person_indices: Indices of person detections
        colors: Dict mapping status to BGR color
        
    Returns:
        Annotated frame
    """
    if colors is None:
        colors = {
            'safe': (0, 255, 0),      # Green
            'unsafe': (0, 165, 255),  # Orange
            'fired': (0, 0, 255)      # Red
        }
    
    annotated = frame.copy()
    
    for idx in person_indices:
        x1, y1, x2, y2 = map(int, boxes[idx])
        track_id = track_ids[idx]
        
        # Default green
        color = colors['safe']
        label = f"ID:{track_id} SAFE"
        
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, label, (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return annotated
