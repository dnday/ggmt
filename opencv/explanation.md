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

---

# Metode Segmentasi Gambar (Dokumentasi segment_image.py)

Program `segment_image.py` kini telah di-upgrade menggunakan metode canggih yang sama dengan `segment_video.py` dan `main.py` untuk memastikan hasil deteksi yang konsisten, halus, dan bebas noise.

## 1. Pre-processing & Noise Reduction (Sama seperti main.py)
Agar hasilnya sehalus `main.py`, kami menerapkan langkah yang sama persis:
*   **Gaussian Blur**: Menghaluskan citra awal untuk membuang bintik-bintik kasar.
*   **Operasi Morfologi (Open/Close)**: Membersihkan noise putih kecil dan menutup lubang hitam pada objek yang terdeteksi.

## 2. Interaksi Pengguna (Click-to-Pick)
Fitur unggulan yang memudahkan pengguna memilih warna target secara langsung.
*   **Klik Kiri**: Mengambil sampel warna Merah dari piksel yang diklik.
*   **Klik Kanan**: Mengambil sampel warna Hijau dari piksel yang diklik.
*   **Auto-Range**: Program secara otomatis menghitung rentang HSV yang optimal (+/- 10 Hue, +/- 40 Sat/Val) berdasarkan warna yang diklik, menangani kasus khusus seperti warna merah yang memiliki dua rentang Hue (0-10 dan 170-180).

## 3. Filter Kebulatan (Circularity Check)
Selain filter warna, program ini juga memverifikasi bentuk objek.
```python
circularity = 4 * np.pi * (area / (perimeter * perimeter))
if circularity > 0.4:
    # Deteksi sebagai bola
```
*   **Tujuan**: Membedakan antara bola (bulat) dengan objek lain yang warnanya mirip tapi bentuknya tidak beraturan (seperti pantulan air yang memanjang).
*   **Ambang Batas (0.4)**: Nilai ini dipilih agar cukup longgar untuk mendeteksi bola yang mungkin terlihat sedikit penyok atau kabur karena jarak, namun tetap cukup ketat untuk membuang noise abstrak.

## 4. Filter Luas Area
```python
if area > 100:
```
*   **Tujuan**: Hanya mendeteksi objek dengan ukuran minimal 100 piksel. Ini sangat efektif untuk menghilangkan "debu" atau noise kecil yang tersisa setelah proses morfologi.

## 5. Tampilan Multi-View (Grid 2x2)
Untuk memudahkan analisis, program menampilkan 4 visualisasi sekaligus:
1.  **Asli**: Gambar original.
2.  **Overlay**: Gambar asli dengan kotak deteksi.
3.  **Masked**: Latar belakang dihitamkan, hanya objek berwarna yang muncul.
4.  **Binary**: Masker hitam-putih murni untuk melihat kualitas segmentasi.
