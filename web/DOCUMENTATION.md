# Dokumentasi Sistem Monitoring Kapal Otonom (USV)

Dokumentasi ini menjelaskan arsitektur, struktur kode, dan cara kerja dari sistem monitoring kapal tanpa awak (Unmanned Surface Vehicle) yang terdiri dari **Backend (Flask/Python)** dan **Frontend (Next.js/React)**.

---

## 1. Arsitektur Sistem

Sistem ini menggunakan arsitektur **Client-Server**:
*   **Backend (Python Flask)**: Bertindak sebagai otak kapal. Mengelola logika navigasi otonom (simulasi), pembacaan sensor, kamera, dan komunikasi data.
*   **Frontend (Next.js)**: Antarmuka pengguna (Dashboard) untuk memantau status kapal secara real-time, mengirim perintah misi, dan melihat feed kamera.

---

## 2. Backend (Server)

**Lokasi Bagian**: `web/backend/`
**Teknologi**: Python, Flask, OpenCV, Threading.

Backend berjalan menggunakan *multithreading* untuk menangani tugas secara paralel:

### A. Core Logic (`app.py`)

File utama ini memiliki 3 komponen utama:

#### 1. Global State (`ship_status`)
Variabel *dictionary* yang menyimpan status terkini kapal (sebagai simulasi *Shared Memory*):
```python
ship_status = {
    "mode": "IDLE",        # Mode operasi: IDLE, AUTONOMOUS, RETURN_TO_HOME
    "battery": 100,        # Baterai (%)
    "speed": 0.0,          # Kecepatan (knots)
    "latitude": -7.150000, # Posisi GPS Latitude
    "longitude": 112.800000, # Posisi GPS Longitude
    "waypoints": [],       # Daftar titik tujuan misi
    ...
}
```

#### 2. Background Threads
Backend menjalankan dua *thread* terpisah agar server tidak *blocking*:
*   **Thread 1: `ship_logic_loop()`**
    *   **Fungsi**: Mensimulasikan perilaku fisik kapal.
    *   **Logika**:
        *   Jika mode `AUTONOMOUS`: Kapal bergerak menuju *waypoints* yang telah diupload menggunakan perhitungan vektor sederhana. Mengurangi baterai seiring waktu.
        *   Jika mode `RETURN_TO_HOME`: Kapal bergerak otomatis kembali ke titik awal.
*   **Thread 2: `camera_loop()`**
    *   **Fungsi**: Mengakses kamera webcam atau file video.
    *   **Logika**: Membaca frame, menambahkan *overlay* teks (Timestamp/Mode), dan menyimpannya ke `static/live.jpg` untuk diakses frontend.

#### 3. API Endpoints
Interface komunikasi HTTP untuk Frontend:

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| **GET** | `/api/telemetry` | Mengambil data JSON status kapal (posisi, baterai, speed, dll). |
| **GET** | `/api/video_feed` | Mengambil gambar JPEG terbaru dari kamera (MJPEG-like). |
| **POST** | `/api/command` | Mengirim perintah kontrol (`START`, `STOP`, `RTH`). |
| **POST** | `/api/waypoints` | Mengirim daftar koordinat misi (*waypoints*) dari Peta ke Kapal. |

---

## 3. Frontend (User Interface)

**Lokasi Bagian**: `web/frontend/`
**Teknologi**: Next.js 14 (App Router), React, Tailwind CSS, Leaflet Map.

Frontend didesain dengan estetika modern (*Dark Mode*, *Glassmorphism*) dan responsif.

### A. Halaman Utama (`app/page.tsx`)
Ini adalah *Dashboard* pusat kontrol (Ground Control Station).

**Fitur Utama**:
1.  **Peta Interaktif (`components/Map.tsx`)**:
    *   Menampilkan posisi kapal (Icon Perahu).
    *   Menampilkan jejak lintasan (*Trail*).
    *   **Input Waypoint**: User bisa klik di peta untuk menambahkan titik tujuan misi.
    *   Menampilkan *Polyline* rencana misi (garis merah).
2.  **Panel Telemetri**:
    *   **Speedometer**: Menampilkan kecepatan kapal dengan *progress bar*.
    *   **Battery Monitor**: Indikator baterai dengan perubahan warna (Hijau/Merah) berdasarkan level.
3.  **Mission Control**:
    *   Tombol **Start Mission**: Mengupload waypoints ke backend dan memulai mode `AUTONOMOUS`.
    *   Tombol **Stop / Idle**: Menghentikan kapal.
    *   Tombol **Return to Home**: Memanggil kapal kembali ke pangkalan.
    *   Akses ke halaman Kamera.

### B. Halaman Kamera (`app/camera/page.tsx`)
Halaman khusus untuk pemantauan visual penuh layar.

**Fitur**:
*   Menampilkan feed video dari backend secara *real-time* (refresh rate 10 FPS).
*   Indikator status "LIVE".
*   Tombol kembali ke Dashboard.

### C. Komponen Peta (`components/Map.tsx`)
Menggunakan library `react-leaflet`.
*   **Dynamic Import**: Diload dengan `ssr: false` di `page.tsx` karena library peta membutuhkan akses `window` browser yang tidak ada di server Next.js.
*   **Layers**: Mendukung tampilan Satelit (Esri World Imagery) dan Laut (Esri Ocean).

---

## 4. Cara Menjalankan Sistem

### Prasyarat
*   Python 3.x (dengan library: `flask`, `flask-cors`, `opencv-python`, `numpy`)
*   Node.js & NPM

### Langkah 1: Jalankan Backend
1.  Buka terminal, masuk ke folder backend:
    ```bash
    cd d:\Dev\Python\boat\web\backend
    ```
2.  Install dependencies (jika belum):
    ```bash
    pip install flask flask-cors opencv-python request
    ```
3.  Jalankan server:
    ```bash
    python app.py
    ```
    *Server akan berjalan di `http://localhost:5000`*

### Langkah 2: Jalankan Frontend
1.  Buka terminal baru, masuk ke folder frontend:
    ```bash
    cd d:\Dev\Python\boat\web\frontend\frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Jalankan development server:
    ```bash
    npm run dev
    ```
4.  Buka browser di `http://localhost:3000`.

---

## 5. Alur Kerja Misi (Workflow)
1.  User membuka Dashboard.
2.  User mengklik beberapa titik di Peta untuk membuat rute misi (*Waypoints*).
3.  User menekan tombol **"Start Mission"**.
4.  **Frontend** mengirim waypoints ke **Backend** (`POST /api/waypoints`) lalu mengirim perintah START (`POST /api/command`).
5.  **Backend** mengubah mode ke `AUTONOMOUS`.
6.  Kapal (simulasi di Backend) mulai bergerak dari titik ke titik.
7.  **Frontend** memantau pergerakan kapal yang terupdate di Peta secara otomatis setiap detik.
