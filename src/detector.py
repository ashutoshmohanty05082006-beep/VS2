from ultralytics import YOLO
import cv2
import json
from typing import List, Dict, Any, Tuple
import numpy as np

class SafetyMonitor:
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """
        Initialize the SafetyMonitor with a YOLO model.

        Args:
            model_path: Path to the trained YOLO model weights.
                       Defaults to yolov8n.pt (pre-trained COCO model).
                       For PPE detection, use a fine-tuned model.
        """
        self.model = YOLO(model_path)
        # Define PPE classes - these should match your dataset classes
        # Adjust these based on your Roboflow dataset
        self.ppe_classes = {
            'helmet': 'helmet',
            'hardhat': 'helmet',  # alias
            'goggles': 'goggles',
            'glasses': 'goggles',  # alias
            'mask': 'mask',
            'gloves': 'gloves',
            'shoes': 'shoes',
            'boots': 'shoes',  # alias
            'vest': 'vest'
        }

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Process a single frame for PPE detection and compliance checking.

        Args:
            frame: Input image/frame as numpy array (BGR format)

        Returns:
            Tuple of (annotated_frame, compliance_data)
            - annotated_frame: Frame with bounding boxes drawn
            - compliance_data: List of dicts with person compliance info
        """
        # Run YOLO tracking (persist=True maintains IDs across frames)
        results = self.model.track(frame, persist=True, verbose=False)

        if results[0].boxes is None:
            return frame, []

        persons = []
        equipment = []

        # Separate persons from equipment
        for box in results[0].boxes:
            cls_id = int(box.cls)
            class_name = self.model.names[cls_id].lower()

            if class_name == 'person':
                persons.append(box)
            elif class_name in self.ppe_classes.values():
                equipment.append(box)

        compliance_data = []

        # Association logic: check PPE for each person
        for person in persons:
            p_id = int(person.id) if person.id is not None else -1
            p_box = person.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]

            # Check for each required PPE item
            violations = []
            detected_ppe = set()

            for eq in equipment:
                eq_box = eq.xyxy[0].cpu().numpy()
                eq_class = self.model.names[int(eq.cls)].lower()

                if self.check_association(p_box, eq_box, eq_class):
                    detected_ppe.add(self.ppe_classes.get(eq_class, eq_class))

            # Check for required PPE (customize based on your safety requirements)
            required_ppe = {'helmet', 'goggles', 'mask', 'gloves', 'shoes'}
            missing_ppe = required_ppe - detected_ppe

            if missing_ppe:
                violations = [f"Missing {item}" for item in missing_ppe]

            # Determine overall status
            status = "Safe" if not violations else "Violation"

            person_status = {
                "id": p_id,
                "bbox": p_box.tolist(),
                "status": status,
                "violations": violations,
                "detected_ppe": list(detected_ppe),
                "timestamp": self._get_timestamp()
            }
            compliance_data.append(person_status)

        # Draw bounding boxes on frame
        annotated_frame = self._draw_annotations(frame, results[0])

        return annotated_frame, compliance_data

    def check_association(self, person_box: np.ndarray, item_box: np.ndarray, item_class: str) -> bool:
        """
        Check if PPE item is associated with the person using spatial reasoning.

        Args:
            person_box: [x1, y1, x2, y2] person bounding box
            item_box: [x1, y1, x2, y2] PPE item bounding box
            item_class: Class name of the PPE item

        Returns:
            True if item is associated with person
        """
        px1, py1, px2, py2 = person_box
        ix1, iy1, ix2, iy2 = item_box

        person_width = px2 - px1
        person_height = py2 - py1

        # Item center
        cx, cy = (ix1 + ix2) / 2, (iy1 + iy2) / 2

        # Spatial rules based on PPE type
        if item_class in ['helmet', 'hardhat']:
            # Helmet should be in top 1/3 of person
            top_third = py1 + person_height / 3
            return py1 <= cy <= top_third and px1 <= cx <= px2

        elif item_class in ['shoes', 'boots']:
            # Shoes should be in bottom 1/5 of person
            bottom_fifth = py2 - person_height / 5
            return bottom_fifth <= cy <= py2 and px1 <= cx <= px2

        elif item_class in ['goggles', 'glasses']:
            # Goggles typically in upper middle of face
            upper_middle = py1 + person_height * 0.4
            return py1 <= cy <= upper_middle and px1 <= cx <= px2

        elif item_class in ['mask']:
            # Mask around face area
            face_area_top = py1 + person_height * 0.2
            face_area_bottom = py1 + person_height * 0.5
            return face_area_top <= cy <= face_area_bottom and px1 <= cx <= px2

        elif item_class in ['gloves']:
            # Gloves are harder to associate spatially, use IoU or proximity
            return self._calculate_iou(person_box, item_box) > 0.1

        elif item_class in ['vest']:
            # Vest should overlap with torso area
            torso_top = py1 + person_height * 0.2
            torso_bottom = py1 + person_height * 0.7
            return torso_top <= cy <= torso_bottom and px1 <= cx <= px2

        else:
            # Default: check if item center is inside person box
            return px1 <= cx <= px2 and py1 <= cy <= py2

    def _calculate_iou(self, box1: np.ndarray, box2: np.ndarray) -> float:
        """Calculate Intersection over Union between two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

    def _draw_annotations(self, frame: np.ndarray, results) -> np.ndarray:
        """Draw bounding boxes and labels on the frame."""
        annotated_frame = frame.copy()

        if results.boxes is not None:
            for box in results.boxes:
                cls_id = int(box.cls)
                class_name = self.model.names[cls_id]

                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                # Color based on class (person vs PPE)
                if class_name.lower() == 'person':
                    color = (0, 255, 0)  # Green for persons
                    # Add ID if tracking is active
                    if box.id is not None:
                        label = f"Person {int(box.id)}"
                    else:
                        label = "Person"
                else:
                    color = (0, 0, 255)  # Red for PPE
                    label = class_name

                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                # Draw label
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return annotated_frame

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()

    def process_video(self, video_path: str, output_path: str = None) -> List[Dict[str, Any]]:
        """
        Process a video file and return compliance data for all frames.

        Args:
            video_path: Path to input video file
            output_path: Optional path to save annotated video

        Returns:
            List of compliance data dictionaries
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        all_compliance_data = []

        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            annotated_frame, compliance_data = self.process_frame(frame)

            # Add frame number to compliance data
            for person_data in compliance_data:
                person_data['frame'] = frame_count

            all_compliance_data.extend(compliance_data)

            if output_path:
                out.write(annotated_frame)

            frame_count += 1

        cap.release()
        if output_path:
            out.release()

        return all_compliance_data