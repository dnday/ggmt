import cv2
import numpy as np

def empty(a):
    pass

# Load Video
cap = cv2.VideoCapture('VIDEONYAA.mp4')

# Buat Window untuk Trackbar
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 640, 400)

# Trackbar untuk Hijau - UNTUK HIJAU GELAP
cv2.createTrackbar("Hue Min Green", "Trackbars", 35, 179, empty)
cv2.createTrackbar("Hue Max Green", "Trackbars", 90, 179, empty)
cv2.createTrackbar("Sat Min Green", "Trackbars", 20, 255, empty)
cv2.createTrackbar("Sat Max Green", "Trackbars", 255, 255, empty)
cv2.createTrackbar("Val Min Green", "Trackbars", 20, 255, empty)
cv2.createTrackbar("Val Max Green", "Trackbars", 255, 255, empty)

# Trackbar untuk Brightness Adjustment
cv2.createTrackbar("Brightness", "Trackbars", 30, 100, empty)

# Trackbar untuk Merah - Range lebih longgar untuk deteksi bola
cv2.createTrackbar("Hue Min Red", "Trackbars", 0, 179, empty)
cv2.createTrackbar("Hue Max Red", "Trackbars", 10, 179, empty)
cv2.createTrackbar("Sat Min Red", "Trackbars", 80, 255, empty)
cv2.createTrackbar("Sat Max Red", "Trackbars", 255, 255, empty)
cv2.createTrackbar("Val Min Red", "Trackbars", 80, 255, empty)
cv2.createTrackbar("Val Max Red", "Trackbars", 255, 255, empty)

# Trackbar untuk Filter
cv2.createTrackbar("Min Area", "Trackbars", 500, 5000, empty)
cv2.createTrackbar("Max Area", "Trackbars", 10000, 15000, empty)
cv2.createTrackbar("Circularity x10", "Trackbars", 4, 10, empty)

while True:
    success, img = cap.read()
    if not success:
        # Reset video ke awal jika sudah selesai
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
        
    img = cv2.resize(img, (640, 480))
    
    # Brightness adjustment untuk warna gelap
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
    
    # Range Merah (range bawah)
    lower_red1 = np.array([h_min_red, s_min_red, v_min_red])
    upper_red1 = np.array([h_max_red, s_max_red, v_max_red])
    # Range Merah (range atas 170-180)
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
    
    # Pembersihan Noise - Lebih agresif
    kernel = np.ones((5, 5), np.uint8)
    maskGreen = cv2.morphologyEx(maskGreen, cv2.MORPH_OPEN, kernel, iterations=2)
    maskGreen = cv2.morphologyEx(maskGreen, cv2.MORPH_CLOSE, kernel, iterations=3)
    maskRed = cv2.morphologyEx(maskRed, cv2.MORPH_OPEN, kernel, iterations=2)
    maskRed = cv2.morphologyEx(maskRed, cv2.MORPH_CLOSE, kernel, iterations=3)
    
    maskTotal = cv2.bitwise_or(maskGreen, maskRed)
    
    # Deteksi Kontur untuk HIJAU
    contoursGreen, _ = cv2.findContours(maskGreen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Deteksi Kontur untuk MERAH
    contoursRed, _ = cv2.findContours(maskRed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    imgResult = img.copy()
    
    # Proses kontur HIJAU
    for cnt in contoursGreen:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Hitung compactness tambahan
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Filter: circularity, aspect ratio, solidity
                if circularity > circularity_thresh and 0.5 < aspect_ratio < 2.0 and solidity > 0.7:
                    cv2.drawContours(imgResult, [cnt], -1, (0, 255, 0), 2)
                    cv2.rectangle(imgResult, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    # Tampilkan info untuk debugging
                    text = f"HIJAU C:{circularity:.2f} S:{solidity:.2f}"
                    cv2.putText(imgResult, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
    
    # Proses kontur MERAH
    for cnt in contoursRed:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            perimeter = cv2.arcLength(cnt, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Hitung compactness tambahan
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Filter lebih longgar untuk merah: circularity rendah, aspect ratio lebar, solidity rendah
                if circularity > circularity_thresh and 0.5 < aspect_ratio < 2.0 and solidity > 0.7:
                    cv2.drawContours(imgResult, [cnt], -1, (0, 0, 255), 2)
                    cv2.rectangle(imgResult, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    # Tampilkan info untuk debugging
                    text = f"MERAH C:{circularity:.2f} S:{solidity:.2f}"
                    cv2.putText(imgResult, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)
    
    # Tampilkan hasil
    cv2.imshow("Original", img)
    cv2.imshow("Mask Hijau", maskGreen)
    cv2.imshow("Mask Merah", maskRed)
    cv2.imshow("Mask Total", maskTotal)
    cv2.imshow("Result - Segmentasi Bola", imgResult)
    
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
