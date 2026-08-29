#!/usr/bin/env python3
"""
Snap & Detect Flask Web Application
Button-triggered single frame detection for debugging
"""

import time
import numpy as np
from picamera2 import Picamera2
import cv2
from ultralytics import YOLO
from flask import Flask, render_template, Response, jsonify, request
import base64

# Configuration
MODEL_PATH = "weights/best.pt"
CONFIDENCE_THRESHOLD = 0.25
FRAME_SIZE = (640, 640)

# Class names
CLASS_NAMES = {
    0: "raw",
    1: "ripe", 
    2: "rotten"
}

# Flask app
app = Flask(__name__)

# Global variables
picam2 = None
model = None
is_running = False

def load_model():
    """Load the YOLOv8 model"""
    global model
    print(f"Loading model from {MODEL_PATH}...")
    try:
        model = YOLO(MODEL_PATH)
        print(f"Model loaded successfully! Classes: {model.names}")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def setup_camera():
    """Initialize the Raspberry Pi camera"""
    global picam2
    print("Initializing camera...")
    try:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(
            main={"size": FRAME_SIZE, "format": "RGB888"},
            controls={"FrameRate": 10}
        )
        picam2.configure(config)
        picam2.start()
        print("Camera initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False

def generate_frames():
    """Generate video frames for live preview"""
    while is_running:
        try:
            frame = picam2.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Frame generation error: {e}")
            time.sleep(0.1)

@app.route('/')
def index():
    """Render the main page with snap button"""
    return render_template('snap.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route for live preview"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snap_and_detect', methods=['POST'])
def snap_and_detect():
    """Capture a single frame and run detection"""
    try:
        # Capture single frame
        frame = picam2.capture_array()
        
        # Save frame for debugging
        cv2.imwrite("debug_snap.jpg", frame)
        
        # Run inference
        results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=True)
        
        # Process detections
        detections = []
        annotated_frame = frame.copy()
        
        for result in results:
            print(f"Model returned {len(result.boxes)} boxes")
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_name = CLASS_NAMES.get(class_id, f"Unknown_{class_id}")
                    
                    # Get bounding box
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Draw on frame
                    if class_name == "ripe":
                        color = (0, 255, 0)  # Green
                    elif class_name == "raw":
                        color = (255, 255, 0)  # Yellow
                    elif class_name == "rotten":
                        color = (0, 0, 255)  # Red
                    else:
                        color = (255, 0, 0)  # Blue
                    
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{class_name}: {confidence:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    detections.append({
                        'class': class_name,
                        'confidence': confidence,
                        'class_id': class_id
                    })
        
        # Save annotated frame
        cv2.imwrite("debug_snap_annotated.jpg", annotated_frame)
        
        # Convert annotated frame to base64 for display
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        img_str = base64.b64encode(buffer).decode()
        
        return jsonify({
            'success': True,
            'detections': detections,
            'image': img_str,
            'debug_info': {
                'frame_shape': frame.shape,
                'frame_stats': {
                    'min': int(frame.min()),
                    'max': int(frame.max()),
                    'mean': float(frame.mean())
                },
                'num_results': len(results),
                'total_detections': len(detections)
            }
        })
        
    except Exception as e:
        print(f"Error in snap_and_detect: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })

def main():
    """Main function to start the application"""
    global is_running
    
    print("=" * 50)
    print("Snap & Detect Lime Classification")
    print("=" * 50)
    
    # Load model
    if not load_model():
        print("Failed to load model. Exiting.")
        return
    
    # Setup camera
    if not setup_camera():
        print("Failed to initialize camera. Exiting.")
        return
    
    is_running = True
    
    print("Starting Flask server on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        is_running = False
        if picam2:
            picam2.stop()
        print("Camera stopped. System shutdown.")

if __name__ == "__main__":
    main()