# object_detection_yolov5.py

import torch
import logging
import cv2

class ObjectDetectionYOLOv5:
    """
    Handles object detection using the YOLOv5 model.
    """
    def __init__(self, model_name='yolov5s', pretrained=True):
        """
        Initializes the YOLOv5 model.

        :param model_name: Name of the YOLOv5 model variant (e.g., 'yolov5s', 'yolov5m', etc.).
        :param pretrained: Whether to load pretrained weights.
        """
        self.model = None
        self.load_model(model_name, pretrained)
    
    def load_model(self, model_name='yolov5s', pretrained=True):
        """
        Loads the YOLOv5 model from Ultralytics repository.

        :param model_name: Name of the YOLOv5 model variant.
        :param pretrained: Whether to load pretrained weights.
        """
        try:
            self.model = torch.hub.load('ultralytics/yolov5', model_name, pretrained=pretrained)
            self.model.eval()
            logging.info(f"{model_name} model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading YOLOv5 model: {e}")
            raise e
    
    def detect_objects(self, image):
        """
        Performs object detection on the provided image.

        :param image: Image in BGR format (as read by OpenCV).
        :return: Tuple containing:
                 - Image with bounding boxes and labels drawn.
                 - List of bounding boxes, each as a dictionary with 'xmin', 'xmax', 'ymin', 'ymax'.
        """
        try:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.model(img_rgb)
            results.render()  # Draws boxes and labels on the image
            detected_img = results.ims[0]
            
            # Extract bounding boxes
            bounding_boxes = []
            for *box, conf, cls in results.xyxy[0].tolist():
                bounding_box = {
                    'xmin': int(box[0]),
                    'ymin': int(box[1]),
                    'xmax': int(box[2]),
                    'ymax': int(box[3]),
                    'confidence': float(conf),
                    'class': int(cls)
                }
                bounding_boxes.append(bounding_box)
            
            return detected_img, bounding_boxes
        except Exception as e:
            logging.error(f"Error during object detection: {e}")
            raise e
