# Metode Segmentasi Warna (Dokumentasi main.py)

Berikut adalah metode yang diterapkan dalam `main.py` untuk menghasilkan citra deteksi yang halus dan bebas noise:

## 1. Pre-processing: Gaussian Blur
Sebelum masuk ke proses deteksi warna, citra asli diproses menggunakan filter **Gaussian Blur**.
```python
blurred = cv2.GaussianBlur(img, (11, 11), 0)
```
*   **Tujuan**: Menghilangkan *high-frequency noise* (bintik-bintik kasar) dan menghaluskan tekstur gambar.
*   **Hasil**: Warna objek menjadi lebih solid/rata, sehingga lebih mudah dideteksi oleh filter HSV.

## 2. Konversi Ruang Warna HSV
Citra dikonversi dari BGR (Blue-Green-Red) ke **HSV (Hue-Saturation-Value)**.
```python
imgHSV = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
```
*   **Tujuan**: Memisahkan informasi warna (Hue) dari intensitas cahaya (Value).
*   **Hasil**: Deteksi warna menjadi lebih konsisten meskipun kondisi pencahayaan berubah-ubah (misal: ada bayangan atau cahaya terang).

## 3. Thresholding (Masking)
Membuat masker biner berdasarkan rentang nilai HSV yang diatur melalui Trackbar.
```python
mask = cv2.inRange(imgHSV, lower, upper)
```
*   **Tujuan**: Mengisolasi piksel yang memiliki warna sesuai target (Merah/Hijau).

## 4. Operasi Morfologi (Noise Removal)
Ini adalah langkah kunci untuk mendapatkan hasil yang "bersih".
```python
kernel = np.ones((7, 7), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
```
*   **Morphological OPEN**: Mengikis (erode) lalu menebalkan (dilate). Efektif untuk **menghilangkan noise bintik-bintik putih kecil** di latar belakang (misal: pantulan cahaya kecil).
*   **Morphological CLOSE**: Menebalkan (dilate) lalu mengikis (erode). Efektif untuk **menutup lubang-lubang hitam kecil** di dalam objek yang terdeteksi, sehingga hasil deteksi menjadi utuh/padat.

Dengan kombinasi **Gaussian Blur** (di awal) dan **Morfologi** (di akhir), hasil deteksi di `main.py` menjadi sangat halus dan minim gangguan (noise).
