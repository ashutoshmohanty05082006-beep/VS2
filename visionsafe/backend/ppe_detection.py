"""
PPE detection logic: Determine missing gear based on detections.
Spatial reasoning for PPE association with persons.
"""

import numpy as np
from typing import List, Tuple


def get_missing_gear(person_box: np.ndarray, ppe_boxes: np.ndarray, 
                     ppe_classes: np.ndarray) -> List[str]:
    """
    Determine missing PPE items for a detected person.
    
    Args:
        person_box: [x1, y1, x2, y2] person bounding box
        ppe_boxes: Array of PPE bounding boxes
        ppe_classes: Array of PPE class IDs
        
    Returns:
        List of missing PPE items
    """
    detected_gear = set()
    
    # Map class IDs to PPE names
    class_mapping = {
        1: 'Helmet',
        2: 'Welding Helmet',
        3: 'Goggles',
        4: 'Vest',
        5: 'Gloves',
        6: 'Shoes'
    }
    
    # Check spatial association with detected PPE
    for ppe_box, ppe_class in zip(ppe_boxes, ppe_classes):
        if is_associated(person_box, ppe_box, int(ppe_class)):
            gear_name = class_mapping.get(int(ppe_class), f"Class_{ppe_class}")
            detected_gear.add(gear_name)
    
    # Determine missing items
    missing = []
    required_ppe = {
        'Vest': 'Vest',
        'Gloves': 'Gloves',
        'Shoes': 'Shoes'
    }
    
    for gear, label in required_ppe.items():
        if label not in detected_gear:
            missing.append(label)
    
    # Check for head protection (any of: Helmet, Welding Helmet, Goggles)
    has_head_protection = any(gear in detected_gear 
                              for gear in ['Helmet', 'Welding Helmet', 'Goggles'])
    if not has_head_protection:
        missing.append('Headgear')
    
    return missing


def is_associated(person_box: np.ndarray, item_box: np.ndarray, 
                  item_class: int) -> bool:
    """
    Check if PPE item is spatially associated with person using rules.
    
    Args:
        person_box: [x1, y1, x2, y2] person bounding box
        item_box: [x1, y1, x2, y2] PPE item bounding box
        item_class: Class ID of PPE item
        
    Returns:
        True if item is associated with person
    """
    px1, py1, px2, py2 = person_box
    ix1, iy1, ix2, iy2 = item_box
    
    person_width = px2 - px1
    person_height = py2 - py1
    
    # Item center
    cx, cy = (ix1 + ix2) / 2, (iy1 + iy2) / 2
    
    # Spatial rules by class
    if item_class in [1, 2]:  # Helmet, Welding Helmet
        # Should be in top 1/3 of person
        top_third = py1 + person_height / 3
        return py1 <= cy <= top_third and px1 <= cx <= px2
    
    elif item_class == 6:  # Shoes
        # Should be in bottom 1/5 of person
        bottom_fifth = py2 - person_height / 5
        return bottom_fifth <= cy <= py2 and px1 <= cx <= px2
    
    elif item_class == 3:  # Goggles
        # In upper middle of face
        upper_middle = py1 + person_height * 0.4
        return py1 <= cy <= upper_middle and px1 <= cx <= px2
    
    elif item_class == 4:  # Vest
        # Overlaps with torso
        torso_top = py1 + person_height * 0.2
        torso_bottom = py1 + person_height * 0.7
        return torso_top <= cy <= torso_bottom and px1 <= cx <= px2
    
    elif item_class == 5:  # Gloves
        # Use IoU for gloves (harder to associate spatially)
        return calculate_iou(person_box, item_box) > 0.1
    
    else:
        # Default: check if item center is inside person box
        return px1 <= cx <= px2 and py1 <= cy <= py2


def calculate_iou(box1: np.ndarray, box2: np.ndarray) -> float:
    """Calculate Intersection over Union between two boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0
