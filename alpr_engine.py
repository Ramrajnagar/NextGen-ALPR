import cv2
import easyocr
import numpy as np
from ultralytics import YOLO
import os

class AFACSEngine:
    def __init__(self):
        print("Loading YOLOv8 model...")
        self.yolo_model = YOLO('yolov8n.pt') 
        
        print("Loading EasyOCR model...")
        self.reader = easyocr.Reader(['en'], gpu=False)

    def process_image(self, image_path_or_bytes):
        if isinstance(image_path_or_bytes, str):
            img = cv2.imread(image_path_or_bytes)
        else:
            nparr = np.frombuffer(image_path_or_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return None, "Error loading image"

        results = self.yolo_model(img, classes=[2, 3, 5, 7], verbose=False)
        
        plates_found = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                vehicle_crop = img[y1:y2, x1:x2]
                h, w, _ = vehicle_crop.shape
                
                # Crop bottom half assuming plate is there
                lower_crop = vehicle_crop[int(h*0.5):h, 0:w]
                
                if lower_crop.size == 0:
                    continue

                ocr_results = self.reader.readtext(lower_crop)
                
                for (bbox, text, prob) in ocr_results:
                    clean_text = "".join(e for e in text if e.isalnum()).upper()
                    
                    if 3 <= len(clean_text) <= 10 and prob > 0.1:
                        plates_found.append({
                            "text": clean_text,
                            "confidence": prob,
                            "vehicle_bbox": [x1, y1, x2, y2]
                        })
                        
        plates_found = sorted(plates_found, key=lambda x: x['confidence'], reverse=True)
        
        out_img = img.copy()
        best_plate = None
        
        if plates_found:
            best_plate = plates_found[0]
            bx1, by1, bx2, by2 = best_plate['vehicle_bbox']
            
            cv2.rectangle(out_img, (bx1, by1), (bx2, by2), (0, 255, 0), 3)
            
            label = f"PLATE: {best_plate['text']}"
            cv2.putText(out_img, label, (bx1, max(30, by1 - 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
        return out_img, plates_found

if __name__ == "__main__":
    engine = AFACSEngine()
    print("Engine loaded successfully.")
    
    test_img_path = "data/sample_car_1.jpg"
    if os.path.exists(test_img_path):
        print(f"Testing on {test_img_path}...")
        out_img, plates = engine.process_image(test_img_path)
        if plates:
            print(f"Found plates: {plates}")
            cv2.imwrite("data/test_output.jpg", out_img)
            print("Saved output to data/test_output.jpg")
        else:
            print("No plates found in test image.")
