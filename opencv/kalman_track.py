import cv2
import numpy as np

class KalmanBallTracker:
    def __init__(self):
        # Kalman Filter untuk tracking posisi bola (x, y, vx, vy)
        self.kalman = cv2.KalmanFilter(4, 2)  # 4 state variables, 2 measurement variables
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                                   [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                                  [0, 1, 0, 1],
                                                  [0, 0, 1, 0],
                                                  [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
        self.kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1
        self.predicted = None
        self.measured = None
        
    def predict(self):
        self.predicted = self.kalman.predict()
        return (int(self.predicted[0]), int(self.predicted[1]))
    
    def update(self, measurement):
        self.measured = np.array([[np.float32(measurement[0])],
                                  [np.float32(measurement[1])]])
        self.kalman.correct(self.measured)
        return measurement

def empty(a):
    pass

# Load Video
cap = cv2.VideoCapture('VIDEONYAA.mp4')

# Buat Window untuk Trackbar
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 640, 400)

# Trackbar untuk Hijau
cv2.createTrackbar("Hue Min Green", "Trackbars", 35, 179, empty)
cv2.createTrackbar("Hue Max Green", "Trackbars", 90, 179, empty)
cv2.createTrackbar("Sat Min Green", "Trackbars", 20, 255, empty)
cv2.createTrackbar("Sat Max Green", "Trackbars", 255, 255, empty)
cv2.createTrackbar("Val Min Green", "Trackbars", 20, 255, empty)
cv2.createTrackbar("Val Max Green", "Trackbars", 255, 255, empty)

# Trackbar untuk Merah
cv2.createTrackbar("Hue Min Red", "Trackbars", 0, 179, empty)
cv2.createTrackbar("Hue Max Red", "Trackbars", 10, 179, empty)
cv2.createTrackbar("Sat Min Red", "Trackbars", 80, 255, empty)
cv2.createTrackbar("Sat Max Red", "Trackbars", 255, 255, empty)
cv2.createTrackbar("Val Min Red", "Trackbars", 80, 255, empty)
cv2.createTrackbar("Val Max Red", "Trackbars", 255, 255, empty)

# Trackbar untuk Brightness
cv2.createTrackbar("Brightness", "Trackbars", 30, 100, empty)

# Trackbar untuk Filter
cv2.createTrackbar("Min Area", "Trackbars", 500, 5000, empty)
cv2.createTrackbar("Max Area", "Trackbars", 10000, 15000, empty)
cv2.createTrackbar("Circularity x10", "Trackbars", 4, 10, empty)

# Inisialisasi Kalman Tracker untuk setiap bola
tracker_green = KalmanBallTracker()
tracker_red = KalmanBallTracker()

# Variabel untuk tracking
green_detected = False
red_detected = False
green_trail = []
red_trail = []
max_trail_length = 30

while True:
    success, img = cap.read()
    if not success:
        # Reset video ke awal jika sudah selesai
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        green_trail.clear()
        red_trail.clear()
        tracker_green = KalmanBallTracker()
        tracker_red = KalmanBallTracker()
        continue
        
    img = cv2.resize(img, (640, 480))
    
    # Brightness adjustment
    brightness = cv2.getTrackbarPos("Brightness", "Trackbars")
    if brightness > 0:
        img = cv2.convertScaleAbs(img, alpha=1.0, beta=brightness)
    
    # Blur untuk mengurangi noise
    imgBlur = cv2.GaussianBlur(img, (5, 5), 0)
    imgHSV = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)
    
    # Ambil nilai dari trackbar untuk Hijau
    h_min_green = cv2.getTrackbarPos("Hue Min Green", "Trackbars")
    h_max_green = cv2.getTrackbarPos("Hue Max Green", "Trackbars")
    s_min_green = cv2.getTrackbarPos("Sat Min Green", "Trackbars")
    s_max_green = cv2.getTrackbarPos("Sat Max Green", "Trackbars")
    v_min_green = cv2.getTrackbarPos("Val Min Green", "Trackbars")
    v_max_green = cv2.getTrackbarPos("Val Max Green", "Trackbars")
    
    # Ambil nilai dari trackbar untuk Merah
    h_min_red = cv2.getTrackbarPos("Hue Min Red", "Trackbars")
    h_max_red = cv2.getTrackbarPos("Hue Max Red", "Trackbars")
    s_min_red = cv2.getTrackbarPos("Sat Min Red", "Trackbars")
    s_max_red = cv2.getTrackbarPos("Sat Max Red", "Trackbars")
    v_min_red = cv2.getTrackbarPos("Val Min Red", "Trackbars")
    v_max_red = cv2.getTrackbarPos("Val Max Red", "Trackbars")
    
    # Range Hijau
    lower_green = np.array([h_min_green, s_min_green, v_min_green])
    upper_green = np.array([h_max_green, s_max_green, v_max_green])
    
    # Range Merah
    lower_red1 = np.array([h_min_red, s_min_red, v_min_red])
    upper_red1 = np.array([h_max_red, s_max_red, v_max_red])
    lower_red2 = np.array([170, s_min_red, v_min_red])
    upper_red2 = np.array([180, s_max_red, v_max_red])
    
    # Buat Mask
    maskGreen = cv2.inRange(imgHSV, lower_green, upper_green)
    maskRed1 = cv2.inRange(imgHSV, lower_red1, upper_red1)
    maskRed2 = cv2.inRange(imgHSV, lower_red2, upper_red2)
    maskRed = cv2.bitwise_or(maskRed1, maskRed2)
    
    # Ambil parameter filter dari trackbar
    min_area = cv2.getTrackbarPos("Min Area", "Trackbars")
    max_area = cv2.getTrackbarPos("Max Area", "Trackbars")
    circularity_thresh = cv2.getTrackbarPos("Circularity x10", "Trackbars") / 10.0
    
    # Pembersihan Noise
    kernel = np.ones((5, 5), np.uint8)
    maskGreen = cv2.morphologyEx(maskGreen, cv2.MORPH_OPEN, kernel, iterations=2)
    maskGreen = cv2.morphologyEx(maskGreen, cv2.MORPH_CLOSE, kernel, iterations=3)
    maskRed = cv2.morphologyEx(maskRed, cv2.MORPH_OPEN, kernel, iterations=2)
    maskRed = cv2.morphologyEx(maskRed, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    maskTotal = cv2.bitwise_or(maskGreen, maskRed)
    
    # Deteksi Kontur
    contoursGreen, _ = cv2.findContours(maskGreen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contoursRed, _ = cv2.findContours(maskRed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    imgResult = img.copy()
    
    # Proses kontur HIJAU dengan Kalman Filter
    green_detected_now = False
    best_green = None
    best_green_area = 0
    
    for cnt in contoursGreen:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                if circularity > circularity_thresh and 0.5 < aspect_ratio < 2.0 and solidity > 0.7:
                    # Pilih kontur terbesar sebagai bola hijau utama
                    if area > best_green_area:
                        best_green_area = area
                        center_x = x + w // 2
                        center_y = y + h // 2
                        best_green = (center_x, center_y, w, h, circularity, solidity)
    
    # Update Kalman untuk hijau
    if best_green:
        center_x, center_y, w, h, circ, sol = best_green
        measured_pos = tracker_green.update((center_x, center_y))
        green_detected_now = True
        green_detected = True
        
        # Tambah ke trail
        green_trail.append((center_x, center_y))
        if len(green_trail) > max_trail_length:
            green_trail.pop(0)
        
        # Gambar deteksi
        cv2.circle(imgResult, (center_x, center_y), 5, (0, 255, 0), -1)
        cv2.rectangle(imgResult, (center_x - w//2, center_y - h//2), 
                     (center_x + w//2, center_y + h//2), (0, 255, 0), 2)
        cv2.putText(imgResult, f"HIJAU C:{circ:.2f}", (center_x - w//2, center_y - h//2 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Prediksi posisi hijau jika tidak terdeteksi
    if green_detected and not green_detected_now:
        predicted_pos = tracker_green.predict()
        cv2.circle(imgResult, predicted_pos, 5, (0, 200, 0), 2)
        cv2.putText(imgResult, "PREDICTED", (predicted_pos[0] - 40, predicted_pos[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 0), 1)
    
    # Proses kontur MERAH dengan Kalman Filter
    red_detected_now = False
    best_red = None
    best_red_area = 0
    
    for cnt in contoursRed:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                if circularity > circularity_thresh and 0.5 < aspect_ratio < 2.0 and solidity > 0.7:
                    # Pilih kontur terbesar sebagai bola merah utama
                    if area > best_red_area:
                        best_red_area = area
                        center_x = x + w // 2
                        center_y = y + h // 2
                        best_red = (center_x, center_y, w, h, circularity, solidity)
    
    # Update Kalman untuk merah
    if best_red:
        center_x, center_y, w, h, circ, sol = best_red
        measured_pos = tracker_red.update((center_x, center_y))
        red_detected_now = True
        red_detected = True
        
        # Tambah ke trail
        red_trail.append((center_x, center_y))
        if len(red_trail) > max_trail_length:
            red_trail.pop(0)
        
        # Gambar deteksi
        cv2.circle(imgResult, (center_x, center_y), 5, (0, 0, 255), -1)
        cv2.rectangle(imgResult, (center_x - w//2, center_y - h//2), 
                     (center_x + w//2, center_y + h//2), (0, 0, 255), 2)
        cv2.putText(imgResult, f"MERAH C:{circ:.2f}", (center_x - w//2, center_y - h//2 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Prediksi posisi merah jika tidak terdeteksi
    if red_detected and not red_detected_now:
        predicted_pos = tracker_red.predict()
        cv2.circle(imgResult, predicted_pos, 5, (0, 0, 200), 2)
        cv2.putText(imgResult, "PREDICTED", (predicted_pos[0] - 40, predicted_pos[1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)
    
    # Gambar trail (jejak pergerakan)
    for i in range(1, len(green_trail)):
        thickness = max(1, int(np.sqrt(float(i + 1) / max_trail_length) * 2.5))
        cv2.line(imgResult, green_trail[i - 1], green_trail[i], (0, 255, 0), thickness)
    
    for i in range(1, len(red_trail)):
        thickness = max(1, int(np.sqrt(float(i + 1) / max_trail_length) * 2.5))
        cv2.line(imgResult, red_trail[i - 1], red_trail[i], (0, 0, 255), thickness)
    
    # Gambar garis pembatas lintasan jika kedua bola terdeteksi
    if best_green and best_red:
        g_x, g_y = best_green[0], best_green[1]
        r_x, r_y = best_red[0], best_red[1]
        cv2.line(imgResult, (g_x, g_y), (r_x, r_y), (255, 255, 0), 2)
        distance = int(np.sqrt((g_x - r_x)**2 + (g_y - r_y)**2))
        mid_x, mid_y = (g_x + r_x) // 2, (g_y + r_y) // 2
        cv2.putText(imgResult, f"Jarak: {distance}px", (mid_x - 50, mid_y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Tampilkan hasil
    cv2.imshow("Original", img)
    cv2.imshow("Mask Hijau", maskGreen)
    cv2.imshow("Mask Merah", maskRed)
    cv2.imshow("Kalman Tracking - Segmentasi Bola", imgResult)
    
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
