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
    exit()

# Membuat Jendela Kontrol (Trackbar)
cv2.namedWindow("Pengaturan Warna")
cv2.resizeWindow("Pengaturan Warna", 640, 240)

# Membuat Slider (Nilai awal diset agar rentang warna terlihat luas dulu)
cv2.createTrackbar("Hue Min", "Pengaturan Warna", 0, 179, empty)
cv2.createTrackbar("Hue Max", "Pengaturan Warna", 179, 179, empty)
cv2.createTrackbar("Sat Min", "Pengaturan Warna", 0, 255, empty)   # Saturation 0 biar semua masuk
cv2.createTrackbar("Sat Max", "Pengaturan Warna", 255, 255, empty)
cv2.createTrackbar("Val Min", "Pengaturan Warna", 0, 255, empty)   # Value 0 biar gelap terang masuk
cv2.createTrackbar("Val Max", "Pengaturan Warna", 255, 255, empty)

print("Program Berjalan. Tekan 'q' pada keyboard untuk keluar.")

# --- BAGIAN 2: LOOP UTAMA (Looping terus menerus) ---
while True:
    # 1. Pre-processing: Gaussian Blur (Haluskan citra)
    blurred = cv2.GaussianBlur(img, (11, 11), 0)
    
    # 2. Konversi gambar ke HSV
    imgHSV = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    # 3. Baca posisi slider saat ini
    h_min = cv2.getTrackbarPos("Hue Min", "Pengaturan Warna")
    h_max = cv2.getTrackbarPos("Hue Max", "Pengaturan Warna")
    s_min = cv2.getTrackbarPos("Sat Min", "Pengaturan Warna")
    s_max = cv2.getTrackbarPos("Sat Max", "Pengaturan Warna")
    v_min = cv2.getTrackbarPos("Val Min", "Pengaturan Warna")
    v_max = cv2.getTrackbarPos("Val Max", "Pengaturan Warna")
    
    # 4. Buat Masking (Filter warna)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHSV, lower, upper)
    
    # 5. Operasi Morfologi (Hilangkan Noise)
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 6. Tampilkan hasil (Warna asli ditimpa mask)
    imgResult = cv2.bitwise_and(img, img, mask=mask)
    
    # Resize agar muat di layar laptop (Opsional)
    imgSmall = cv2.resize(img, (400, 300))
    resSmall = cv2.resize(imgResult, (400, 300))
    
    # Tampilkan side-by-side
    stack = np.hstack([imgSmall, resSmall])
    cv2.imshow("Kiri: Asli | Kanan: Deteksi", stack)
    
    # 7. Tombol Keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()