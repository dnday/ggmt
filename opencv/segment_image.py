import cv2
import numpy as np

# --- BAGIAN 1: INISIALISASI (SETUP) ---
def empty(a):
    pass

# Ganti nama file sesuai file Anda
path_gambar = 'GAMBARNYA NICH.jpg'

# Cek apakah file ada
img = cv2.imread(path_gambar)
if img is None:
    print("ERROR: Gambar tidak ditemukan! Cek nama file atau folder.")
    # Buat gambar dummy jika tidak ada
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.rectangle(img, (50, 50), (250, 350), (0, 0, 255), -1) # Merah
    cv2.rectangle(img, (350, 50), (550, 350), (0, 255, 0), -1) # Hijau

# Resize agar muat di layar
img = cv2.resize(img, (640, 480))

# Membuat Jendela Kontrol (Trackbar)
cv2.namedWindow("Pengaturan Warna")
cv2.resizeWindow("Pengaturan Warna", 1000, 600)

# Trackbar untuk MERAH (Default User: HSV[8, 224, 106])
cv2.createTrackbar("R H Min", "Pengaturan Warna", 0, 179, empty)
cv2.createTrackbar("R H Max", "Pengaturan Warna", 18, 179, empty)
cv2.createTrackbar("R S Min", "Pengaturan Warna", 184, 255, empty)
cv2.createTrackbar("R S Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("R V Min", "Pengaturan Warna", 66, 255, empty)
cv2.createTrackbar("R V Max", "Pengaturan Warna", 255, 255, empty)

# Trackbar untuk HIJAU (Default User: HSV[89, 250, 54])
cv2.createTrackbar("G H Min", "Pengaturan Warna", 79, 179, empty)
cv2.createTrackbar("G H Max", "Pengaturan Warna", 99, 179, empty)
cv2.createTrackbar("G S Min", "Pengaturan Warna", 210, 255, empty)
cv2.createTrackbar("G S Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("G V Min", "Pengaturan Warna", 14, 255, empty)
cv2.createTrackbar("G V Max", "Pengaturan Warna", 255, 255, empty)

print("Program Berjalan. Tekan 'q' pada keyboard untuk keluar.")

# --- BAGIAN 2: LOOP UTAMA ---
while True:
    # 1. Konversi gambar ke HSV
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
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
    imgResult = cv2.bitwise_and(img, img, mask=mask_combined)
    
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
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
