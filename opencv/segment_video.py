import cv2
import numpy as np

# --- BAGIAN 1: INISIALISASI (SETUP) ---
def empty(a):
    pass

# Global variables untuk frame agar bisa diakses mouse callback
current_frame = None

def mouse_callback(event, x, y, flags, param):
    global current_frame
    if current_frame is None:
        return

    if event == cv2.EVENT_LBUTTONDOWN: # Klik Kiri -> Set MERAH
        # Map koordinat klik ke ukuran frame kecil (400x300)
        # Karena kita pakai 2x2 grid, kita ambil modulo-nya saja
        ix = x % 400
        iy = y % 300
        
        if iy >= current_frame.shape[0] or ix >= current_frame.shape[1]: return

        bgr = current_frame[iy, ix]
        hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        print(f"Klik Kiri (MERAH) di ({x}, {y}) -> Frame ({ix}, {iy}) - HSV: {hsv}")
        
        # Set Trackbar Merah
        # Merah di HSV itu unik, dia ada di ujung 0-10 DAN 170-180.
        # Jadi kalau Hue-nya kecil (misal 5) atau besar (misal 175), kita harus set range yang benar.
        
        hue = hsv[0]
        range_hue = 10 # Diperlebar jadi +/- 10
        range_sv = 40  # Diperlebar jadi +/- 40
        
        if hue < 10: # Merah Bawah
            cv2.setTrackbarPos("R H Min", "Pengaturan Warna", 0)
            cv2.setTrackbarPos("R H Max", "Pengaturan Warna", 20)
        elif hue > 170: # Merah Atas
            cv2.setTrackbarPos("R H Min", "Pengaturan Warna", 160)
            cv2.setTrackbarPos("R H Max", "Pengaturan Warna", 179)
        else: # Merah Tengah
            cv2.setTrackbarPos("R H Min", "Pengaturan Warna", max(0, hue - range_hue))
            cv2.setTrackbarPos("R H Max", "Pengaturan Warna", min(179, hue + range_hue))
            
        cv2.setTrackbarPos("R S Min", "Pengaturan Warna", max(0, hsv[1] - range_sv))
        cv2.setTrackbarPos("R S Max", "Pengaturan Warna", 255)
        cv2.setTrackbarPos("R V Min", "Pengaturan Warna", max(0, hsv[2] - range_sv))
        cv2.setTrackbarPos("R V Max", "Pengaturan Warna", 255)
        print("-> Trackbar MERAH diupdate!")

    elif event == cv2.EVENT_RBUTTONDOWN: # Klik Kanan -> Set HIJAU
        # Map koordinat klik
        ix = x % 400
        iy = y % 300
        
        if iy >= current_frame.shape[0] or ix >= current_frame.shape[1]: return

        bgr = current_frame[iy, ix]
        hsv = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        print(f"Klik Kanan (HIJAU) di ({x}, {y}) -> Frame ({ix}, {iy}) - HSV: {hsv}")
        
        # Set Trackbar Hijau
        range_hue = 10 # Diperlebar
        range_sv = 40  # Diperlebar
        
        cv2.setTrackbarPos("G H Min", "Pengaturan Warna", max(0, hsv[0] - range_hue))
        cv2.setTrackbarPos("G H Max", "Pengaturan Warna", min(179, hsv[0] + range_hue))
        cv2.setTrackbarPos("G S Min", "Pengaturan Warna", max(0, hsv[1] - range_sv))
        cv2.setTrackbarPos("G S Max", "Pengaturan Warna", 255)
        cv2.setTrackbarPos("G V Min", "Pengaturan Warna", max(0, hsv[2] - range_sv))
        cv2.setTrackbarPos("G V Max", "Pengaturan Warna", 255)
        print("-> Trackbar HIJAU diupdate!")

# Ganti nama file sesuai file Anda
path_video = 'VIDEONYAA.mp4'

# Cek apakah file ada
cap = cv2.VideoCapture(path_video)
if not cap.isOpened():
    print("ERROR: Video tidak ditemukan! Coba pakai webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Webcam tidak bisa dibuka.")
        exit()

# Membuat Jendela Kontrol (Trackbar)
cv2.namedWindow("Pengaturan Warna")
cv2.resizeWindow("Pengaturan Warna", 1000, 600)

# Trackbar untuk MERAH (Default User: HSV[8, 224, 106])
# Range: Hue +/- 10, Sat/Val +/- 40
cv2.createTrackbar("R H Min", "Pengaturan Warna", 0, 179, empty)
cv2.createTrackbar("R H Max", "Pengaturan Warna", 18, 179, empty)
cv2.createTrackbar("R S Min", "Pengaturan Warna", 184, 255, empty)
cv2.createTrackbar("R S Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("R V Min", "Pengaturan Warna", 66, 255, empty)
cv2.createTrackbar("R V Max", "Pengaturan Warna", 255, 255, empty)

# Trackbar untuk HIJAU (Default User: HSV[89, 250, 54])
# Range: Hue +/- 10, Sat/Val +/- 40
cv2.createTrackbar("G H Min", "Pengaturan Warna", 79, 179, empty)
cv2.createTrackbar("G H Max", "Pengaturan Warna", 99, 179, empty)
cv2.createTrackbar("G S Min", "Pengaturan Warna", 210, 255, empty)
cv2.createTrackbar("G S Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("G V Min", "Pengaturan Warna", 14, 255, empty)
cv2.createTrackbar("G V Max", "Pengaturan Warna", 255, 255, empty)

print("Program Berjalan.")
print("Tekan 'q' untuk keluar.")
print("Tampilan: Kiri-Atas (Asli), Kanan-Atas (Overlay), Kiri-Bawah (Masked), Kanan-Bawah (Binary)")

# --- BAGIAN 2: LOOP UTAMA ---
# Buat window hasil dulu agar bisa diset callback
cv2.namedWindow("Hasil Deteksi")
cv2.setMouseCallback("Hasil Deteksi", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Resize agar muat di layar
    frame = cv2.resize(frame, (640, 480))
    current_frame = frame # Update global frame untuk callback

    # 1. Konversi gambar ke HSV
    # Gaussian Blur untuk mengurangi noise high-frequency (bintik-bintik)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    imgHSV = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # 2. Baca posisi slider MERAH
    r_h_min = cv2.getTrackbarPos("R H Min", "Pengaturan Warna")
    r_h_max = cv2.getTrackbarPos("R H Max", "Pengaturan Warna")
    r_s_min = cv2.getTrackbarPos("R S Min", "Pengaturan Warna")
    r_s_max = cv2.getTrackbarPos("R S Max", "Pengaturan Warna")
    r_v_min = cv2.getTrackbarPos("R V Min", "Pengaturan Warna")
    r_v_max = cv2.getTrackbarPos("R V Max", "Pengaturan Warna")

    # 3. Baca posisi slider HIJAU
    g_h_min = cv2.getTrackbarPos("G H Min", "Pengaturan Warna")
    g_h_max = cv2.getTrackbarPos("G H Max", "Pengaturan Warna")
    g_s_min = cv2.getTrackbarPos("G S Min", "Pengaturan Warna")
    g_s_max = cv2.getTrackbarPos("G S Max", "Pengaturan Warna")
    g_v_min = cv2.getTrackbarPos("G V Min", "Pengaturan Warna")
    g_v_max = cv2.getTrackbarPos("G V Max", "Pengaturan Warna")
    
    # 4. Buat Masking Merah (Handle Wrap-Around)
    # Jika User set H Min > H Max (misal Min 170, Max 10), berarti dia mau ambil merah ujung-ujung
    if r_h_min > r_h_max:
        # Range 1: r_h_min sampai 179
        lower_red1 = np.array([r_h_min, r_s_min, r_v_min])
        upper_red1 = np.array([179, r_s_max, r_v_max])
        mask_red1 = cv2.inRange(imgHSV, lower_red1, upper_red1)
        
        # Range 2: 0 sampai r_h_max
        lower_red2 = np.array([0, r_s_min, r_v_min])
        upper_red2 = np.array([r_h_max, r_s_max, r_v_max])
        mask_red2 = cv2.inRange(imgHSV, lower_red2, upper_red2)
        
        mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    else:
        # Normal
        lower_red = np.array([r_h_min, r_s_min, r_v_min])
        upper_red = np.array([r_h_max, r_s_max, r_v_max])
        mask_red = cv2.inRange(imgHSV, lower_red, upper_red)
    
    # 5. Buat Masking Hijau
    lower_green = np.array([g_h_min, g_s_min, g_v_min])
    upper_green = np.array([g_h_max, g_s_max, g_v_max])
    mask_green = cv2.inRange(imgHSV, lower_green, upper_green)

    # 6. Operasi Morfologi (Pembersihan Noise)
    # Perbesar kernel agar noise kecil hilang
    kernel = np.ones((7, 7), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

    # 7. Gabungkan Mask
    mask_combined = cv2.bitwise_or(mask_red, mask_green)
    
    # 8. Tampilkan hasil
    # Mode 0: Original + Overlay (Kotak/Lingkaran)
    # Mode 1: Masked (Latar Hitam)
    # Mode 2: Binary Mask (Putih Hitam)
    
    imgOverlay = frame.copy() # Untuk Mode 0
    imgMasked = cv2.bitwise_and(frame, frame, mask=mask_combined) # Untuk Mode 1
    
    # Gambar kotak di sekitar bola (Hanya jika bentuknya agak bulat)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_red:
        area = cv2.contourArea(contour)
        if area > 300: # Naikkan lagi biar noise hilang
            # Cek kebulatan (circularity)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            # Jika circularity > 0.6 (Harus lebih bulat)
            if circularity > 0.6:
                x, y, w, h = cv2.boundingRect(contour)
                # Gambar di imgOverlay
                cv2.rectangle(imgOverlay, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(imgOverlay, "MERAH", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                # Gambar di imgMasked juga
                cv2.rectangle(imgMasked, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(imgMasked, "MERAH", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_green:
        area = cv2.contourArea(contour)
        if area > 300: # Naikkan lagi
             # Cek kebulatan (circularity)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            if circularity > 0.6:
                x, y, w, h = cv2.boundingRect(contour)
                # Gambar di imgOverlay
                cv2.rectangle(imgOverlay, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(imgOverlay, "HIJAU", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # Gambar di imgMasked juga
                cv2.rectangle(imgMasked, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(imgMasked, "HIJAU", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Tampilkan window 2x2 Grid
    # Resize semua ke 400x300 agar muat di layar (Total 800x600)
    w, h = 400, 300
    
    frame_small = cv2.resize(frame, (w, h))
    imgOverlay_small = cv2.resize(imgOverlay, (w, h))
    imgMasked_small = cv2.resize(imgMasked, (w, h))
    mask_bgr = cv2.cvtColor(mask_combined, cv2.COLOR_GRAY2BGR)
    mask_small = cv2.resize(mask_bgr, (w, h))

    # Update global frame dengan ukuran kecil agar koordinat klik sesuai
    current_frame = frame_small 
    
    # Susun Grid
    # Baris 1: Asli | Overlay
    row1 = np.hstack([frame_small, imgOverlay_small])
    # Baris 2: Masked | Binary Mask
    row2 = np.hstack([imgMasked_small, mask_small])
    # Gabung Baris
    stack = np.vstack([row1, row2])
    
    cv2.imshow("Hasil Deteksi", stack)
    
    # Tombol Keyboard
    k = cv2.waitKey(30) & 0xFF
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
