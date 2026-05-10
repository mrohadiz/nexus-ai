# 🚀 Nexus AI: Orkes AI Full-Stack Tingkat Lanjut

Nexus AI adalah platform orkestrasi AI yang kuat dan lengkap, dirancang untuk percakapan tingkat lanjut, riset otonom, dan perencanaan tugas. Proyek ini menggabungkan backend FastAPI berkinerja tinggi dengan frontend Next.js modern, dilengkapi dengan memori episodik, pemanggilan alat (tool calling), dan sistem fallback model yang cerdas.

![Nexus AI Architecture](https://img.shields.io/badge/Arsitektur-Fullstack-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)

---

## ✨ Fitur Utama

- **💬 UI Chat Canggih**: Respons streaming real-time dengan antarmuka yang dioptimalkan untuk mode gelap menggunakan `assistant-ui`.
- **🔍 Riset Otonom**: Alat terintegrasi untuk pencarian web real-time (DuckDuckGo), pengambilan URL, dan riset topik mendalam.
- **🧠 Memori Episodik (Mira)**: Sistem penyimpanan dan pemanggilan memori jangka panjang untuk konteks yang persisten di berbagai sesi menggunakan pencarian vektor.
- **🛠️ Pemanggilan Alat Cerdas**: Representasi visual eksekusi alat (Sedang Mengeksekusi → Selesai) dengan detail yang dapat diperluas.
- **🔄 Sistem Auto-Fallback**: Secara otomatis beralih ke model LLM alternatif jika model utama gagal atau mengalami kesalahan.
- **📋 Perencanaan Tugas**: Pemecahan tujuan strategis dan kemampuan perencanaan tugas.
- **🖼️ Dukungan Gambar**: Kemampuan untuk menangani dan memproses data gambar URI dalam percakapan.

---

## 🛠️ Stack Teknologi

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy)
- **Memory**: Mira (Episodic Vector Search dengan `zvec`)
- **LLM Provider**: DuckAI / OpenRouter
- **Orkestrasi**: PM2

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Bahasa**: TypeScript
- **Styling**: Tailwind CSS 4
- **Komponen**: Assistant-UI, Lucide React, Framer Motion

---

## 🚀 Memulai

### Prasyarat
- Python 3.10+
- Node.js & Bun
- PostgreSQL
- PM2 (`npm install -g pm2`)

### 1. Klon Repositori
```bash
git clone <url-repo-anda>
cd nexus-ai
```

### 2. Pengaturan Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Konfigurasi variabel lingkungan Anda
python3 init_local_db.py
```

### 3. Pengaturan Frontend
```bash
cd ../frontend
bun install
# atau
npm install
```

### 4. Konfigurasi
Edit `backend/.env` dengan kredensial Anda:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/nexus_db
OPENROUTER_API_KEY=your_key_here
DUCKAI_URL=http://localhost:3000/v1/chat/completions
```

---

## 🏃 Menjalankan Aplikasi

Nexus AI menggunakan skrip manajemen dan PM2 untuk orkestrasi layanan.

### Menggunakan Skrip Manajemen
```bash
# Jalankan semua layanan
./nexus.sh start

# Periksa status
./nexus.sh status

# Lihat log
./nexus.sh logs

# Hentikan semua layanan
./nexus.sh stop
```

### Mode Pengembangan
Jika Anda ingin menjalankan layanan secara manual untuk pengembangan:

**Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
bun run dev --port 5008
```

---

## 📂 Struktur Proyek

```text
nexus-ai/
├── backend/                # Aplikasi FastAPI
│   ├── logic/              # Layanan AI, memori, dan orkestrator
│   ├── config/             # Konfigurasi Database & aplikasi
│   ├── tools/              # Logika pencarian web dan alat riset
│   └── main.py             # Endpoint API dan entry point
├── frontend/               # Aplikasi Next.js
│   ├── src/app/            # Halaman App router dan API routes
│   ├── src/components/     # Komponen UI (ChatInterface, ToolCallDisplay)
│   └── src/lib/            # Fungsi utilitas
├── nexus.sh                # Skrip orkestrasi utama
└── ecosystem.config.js     # Konfigurasi PM2
```

---

## 🌐 Domain & Akses

Aplikasi ini dikonfigurasi untuk berjalan di:
- **Public URL**: [https://chat.mrohadiz.my.id/](https://chat.mrohadiz.my.id/)
- **Backend API**: `http://localhost:8000`
- **Frontend Port**: `5008`

---

## 🛡️ Keamanan & Performa

- **Manajemen CORS**: Asal (origins) yang diizinkan dapat dikonfigurasi untuk komunikasi frontend-backend yang aman.
- **Streaming SSE**: Pengiriman data yang efisien melalui Server-Sent Events.
- **Fallback Model**: Ketersediaan tinggi melalui logika percobaan ulang model utama dan sekunder.
- **Optimasi Memori**: Memori episodik Mira untuk konteks jangka panjang yang efisien tanpa pembengkakan token.

---

## 📝 Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT.

---

**Dikembangkan dengan ❤️ oleh Tim Nexus AI.**
