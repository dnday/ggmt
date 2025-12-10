# Metode Segmentasi Warna dan Pengurangan Noise

Berikut adalah penjelasan mengenai metode yang digunakan untuk mendapatkan hasil citra yang halus dan bebas noise warna dalam program segmentasi bola merah dan hijau.

## 1. Ruang Warna HSV (Hue, Saturation, Value)
Kami menggunakan ruang warna HSV daripada RGB karena HSV memisahkan informasi warna (Hue) dari intensitas cahaya (Value).
- **Hue (H)**: Merepresentasikan jenis warna (misalnya merah, hijau, biru). Ini sangat berguna untuk mendeteksi objek berwarna di bawah kondisi pencahayaan yang berbeda-beda.
- **Saturation (S)**: Kekayaan warna.
- **Value (V)**: Kecerahan warna.

Dengan menggunakan HSV, kita dapat membuat rentang (threshold) yang lebih robust terhadap perubahan pencahayaan dibandingkan jika kita menggunakan RGB.

## 2. Operasi Morfologi (Morphological Operations)
Untuk mendapatkan hasil yang halus dan bebas dari noise (bintik-bintik kecil), kami menggunakan operasi morfologi:

### a. Opening (Erosi diikuti Dilasi)
`cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)`
- **Fungsi**: Menghilangkan noise kecil (bintik putih) di latar belakang gelap.
- **Cara kerja**: Erosi akan mengikis batas objek depan, sehingga objek kecil (noise) akan hilang. Kemudian dilasi akan mengembalikan ukuran objek utama yang tersisa.

### b. Closing (Dilasi diikuti Erosi)
`cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)`
- **Fungsi**: Menutup lubang kecil di dalam objek depan (bola).
- **Cara kerja**: Dilasi akan memperbesar objek dan menutup lubang-lubang kecil. Erosi kemudian mengembalikan ukuran objek ke bentuk semula.

## 3. Filter Area Kontur
Setelah mendapatkan mask yang bersih, kami mencari kontur objek.
- Kami memfilter kontur berdasarkan **luas area** (`cv2.contourArea`).
- Hanya kontur dengan luas di atas ambang batas tertentu (misalnya 500 piksel) yang dianggap sebagai bola. Ini efektif menghilangkan noise yang mungkin masih tersisa setelah operasi morfologi.

## 4. Gaussian Blur (Opsional/Implisit)
Meskipun tidak secara eksplisit ditambahkan sebagai langkah terpisah di kode utama (karena operasi morfologi sudah cukup efektif), penggunaan `cv2.GaussianBlur` sebelum konversi ke HSV sering digunakan untuk mengurangi high-frequency noise pada gambar asli. Dalam implementasi ini, operasi morfologi `Opening` dan `Closing` sudah cukup ampuh untuk menangani noise pada mask biner.
