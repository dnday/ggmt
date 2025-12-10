from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import cv2
import time
import threading
import numpy as np
import random
import os
import math

app = Flask(__name__)
CORS(app)  # Izinkan frontend mengakses backend

# Status Global Kapal (Simulasi Shared Memory)
ship_status = {
    "mode": "IDLE",       # IDLE, AUTONOMOUS, MANUAL, RETURN
    "battery": 100,       # Persentase
    "speed": 0.0,         # Knots
    "latitude": -7.150000, # Selat Madura (Laut)
    "longitude": 112.800000,
    "last_object": "None",
    "waypoints": [],      # List of [lat, lon]
    "current_wp_index": 0
}

# Pastikan folder static ada
if not os.path.exists('static'):
    os.makedirs('static')

# --- THREAD 1: SIMULASI SENSOR & LOGIKA KAPAL ---
def ship_logic_loop():
    center_lat = -7.150000
    center_lon = 112.800000

    while True:
        # 1. Simulasi Baterai berkurang
        if ship_status["mode"] == "AUTONOMOUS":
            ship_status["battery"] = max(0, ship_status["battery"] - 0.05)
            
            # Logika Waypoint Navigation
            if ship_status["waypoints"] and ship_status["current_wp_index"] < len(ship_status["waypoints"]):
                target = ship_status["waypoints"][ship_status["current_wp_index"]]
                target_lat, target_lon = target[0], target[1]
                
                # Hitung vektor arah
                curr_lat = ship_status["latitude"]
                curr_lon = ship_status["longitude"]
                
                # Jarak sederhana (Euclidean)
                dist = math.sqrt((target_lat - curr_lat)**2 + (target_lon - curr_lon)**2)
                
                if dist < 0.0005: # Jika sudah dekat (< 50m kira-kira)
                    ship_status["current_wp_index"] += 1
                    print(f"Reached Waypoint {ship_status['current_wp_index']}")
                    if ship_status["current_wp_index"] >= len(ship_status["waypoints"]):
                         ship_status["mode"] = "IDLE" # Selesai
                else:
                    # Gerak ke arah target
                    step = 0.0002 # Kecepatan gerak
                    dx = (target_lat - curr_lat) / dist
                    dy = (target_lon - curr_lon) / dist
                    
                    ship_status["latitude"] += dx * step
                    ship_status["longitude"] += dy * step
                    ship_status["speed"] = round(random.uniform(10.0, 15.0), 1)
            else:
                # Jika tidak ada waypoint, diam atau mode lain
                ship_status["speed"] = 0.0

        elif ship_status["mode"] == "RETURN_TO_HOME":
             # Gerak lurus kembali ke center (sederhana)
             ship_status["latitude"] += (center_lat - ship_status["latitude"]) * 0.1
             ship_status["longitude"] += (center_lon - ship_status["longitude"]) * 0.1
             ship_status["speed"] = 5.0
             if abs(ship_status["latitude"] - center_lat) < 0.0001:
                 ship_status["mode"] = "IDLE"
        else:
            ship_status["speed"] = 0.0

        time.sleep(0.5) # Update setiap 0.5 detik

# --- THREAD 2: KAMERA & PEMROSESAN GAMBAR ---
def camera_loop():
    cap = cv2.VideoCapture(0) # Ganti 0 dengan path video jika perlu
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            # Jika kamera error/tidak ada, buat gambar hitam (Dummy)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "NO SIGNAL", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            # Simulasi Deteksi Sederhana
            # Tambahkan Timestamp di video
            cv2.putText(frame, f"MODE: {ship_status['mode']}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(frame, time.strftime("%H:%M:%S"), (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Simpan frame terbaru ke file
        # (Dalam production, lebih baik pakai MJPEG Stream, tapi ini metode file lebih mudah dipahami)
        cv2.imwrite('static/live.jpg', frame)
        time.sleep(0.1) # 10 FPS

# Jalankan Thread di Background
t1 = threading.Thread(target=ship_logic_loop, daemon=True)
t2 = threading.Thread(target=camera_loop, daemon=True)
t1.start()
t2.start()

# --- API ENDPOINTS ---

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify(ship_status)

@app.route('/api/video_feed')
def get_video_feed():
    try:
        return send_file('static/live.jpg', mimetype='image/jpeg')
    except:
        return "Not Ready", 404

@app.route('/api/command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    
    if cmd == "START":
        ship_status["mode"] = "AUTONOMOUS"
    elif cmd == "STOP":
        ship_status["mode"] = "IDLE"
    elif cmd == "RTH":
        ship_status["mode"] = "RETURN_TO_HOME"
        
    return jsonify({"message": f"Command {cmd} Executed", "current_mode": ship_status["mode"]})

@app.route('/api/waypoints', methods=['POST'])
def set_waypoints():
    data = request.json
    waypoints = data.get('waypoints', [])
    ship_status["waypoints"] = waypoints
    ship_status["current_wp_index"] = 0
    print(f"Received {len(waypoints)} waypoints")
    return jsonify({"message": "Waypoints updated", "count": len(waypoints)})

if __name__ == '__main__':
    print("🚀 Backend Server Siap di Port 5000")
    app.run(port=5000, debug=False)