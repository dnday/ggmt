import cv2
import numpy as np

# --- BAGIAN 1: INISIALISASI (SETUP) ---
def empty(a):
    pass

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
cv2.resizeWindow("Pengaturan Warna", 640, 500)

# Trackbar untuk MERAH
cv2.createTrackbar("Merah Hue Min", "Pengaturan Warna", 0, 179, empty)
cv2.createTrackbar("Merah Hue Max", "Pengaturan Warna", 10, 179, empty)
cv2.createTrackbar("Merah Sat Min", "Pengaturan Warna", 100, 255, empty)
cv2.createTrackbar("Merah Sat Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("Merah Val Min", "Pengaturan Warna", 100, 255, empty)
cv2.createTrackbar("Merah Val Max", "Pengaturan Warna", 255, 255, empty)

# Trackbar untuk HIJAU
cv2.createTrackbar("Hijau Hue Min", "Pengaturan Warna", 40, 179, empty)
cv2.createTrackbar("Hijau Hue Max", "Pengaturan Warna", 80, 179, empty)
cv2.createTrackbar("Hijau Sat Min", "Pengaturan Warna", 40, 255, empty)
cv2.createTrackbar("Hijau Sat Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("Hijau Val Min", "Pengaturan Warna", 40, 255, empty)
cv2.createTrackbar("Hijau Val Max", "Pengaturan Warna", 255, 255, empty)

print("Program Berjalan. Tekan 'q' pada keyboard untuk keluar.")

# --- BAGIAN 2: LOOP UTAMA ---
while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Resize agar muat di layar
    frame = cv2.resize(frame, (640, 480))

    # 1. Konversi gambar ke HSV
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Baca posisi slider MERAH
    r_h_min = cv2.getTrackbarPos("Merah Hue Min", "Pengaturan Warna")
    r_h_max = cv2.getTrackbarPos("Merah Hue Max", "Pengaturan Warna")
    r_s_min = cv2.getTrackbarPos("Merah Sat Min", "Pengaturan Warna")
    r_s_max = cv2.getTrackbarPos("Merah Sat Max", "Pengaturan Warna")
    r_v_min = cv2.getTrackbarPos("Merah Val Min", "Pengaturan Warna")
    r_v_max = cv2.getTrackbarPos("Merah Val Max", "Pengaturan Warna")

    # 3. Baca posisi slider HIJAU
    g_h_min = cv2.getTrackbarPos("Hijau Hue Min", "Pengaturan Warna")
    g_h_max = cv2.getTrackbarPos("Hijau Hue Max", "Pengaturan Warna")
    g_s_min = cv2.getTrackbarPos("Hijau Sat Min", "Pengaturan Warna")
    g_s_max = cv2.getTrackbarPos("Hijau Sat Max", "Pengaturan Warna")
    g_v_min = cv2.getTrackbarPos("Hijau Val Min", "Pengaturan Warna")
    g_v_max = cv2.getTrackbarPos("Hijau Val Max", "Pengaturan Warna")
    
    # 4. Buat Masking Merah
    lower_red = np.array([r_h_min, r_s_min, r_v_min])
    upper_red = np.array([r_h_max, r_s_max, r_v_max])
    mask_red = cv2.inRange(imgHSV, lower_red, upper_red)
    
    # 5. Buat Masking Hijau
    lower_green = np.array([g_h_min, g_s_min, g_v_min])
    upper_green = np.array([g_h_max, g_s_max, g_v_max])
    mask_green = cv2.inRange(imgHSV, lower_green, upper_green)

    # 6. Operasi Morfologi (Pembersihan Noise)
    kernel = np.ones((5, 5), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_CLOSE, kernel)

    # 7. Gabungkan Mask
    mask_combined = cv2.bitwise_or(mask_red, mask_green)
    
    # 8. Tampilkan hasil
    imgResult = cv2.bitwise_and(frame, frame, mask=mask_combined)
    
    # Gambar kotak di sekitar bola
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_red:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(imgResult, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(imgResult, "MERAH", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours_green:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(imgResult, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(imgResult, "HIJAU", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Tampilkan window
    cv2.imshow("Hasil Deteksi", imgResult)
    cv2.imshow("Mask Merah", mask_red)
    cv2.imshow("Mask Hijau", mask_green)
    
    # 9. Tombol Keluar
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
