# Google Maps Cafe Lead Scraper & Google Sheets Sync

Alat otomasi berbasis Python untuk mengekstrak, memfilter, dan mengklasifikasikan prospek bisnis cafe dan restoran lokal dari Google Maps ke Google Sheets secara real-time.

Dirancang untuk agensi digital, web developer, dan penyedia jasa pemeliharaan website guna menemukan prospek bisnis yang belum memiliki website resmi atau hanya mengandalkan media sosial.

---

## Fitur Utama

- **Integrasi Google Maps:** Mengambil data tempat secara cepat via endpoint `/maps` Serper.dev tanpa risiko pemblokiran IP atau CAPTCHA.
- **Deteksi Otomatis Status Website:**
  - `Belum Ada Website`: Tempat tidak mencantumkan tautan apapun di profil Google Maps (Target Utama Pembuatan Web Baru).
  - `Hanya Sosmed / Menu Digital`: Tempat mencantumkan Instagram, Linktree, TikTok, atau GoFood pada kolom website (Target Upgrade Web Resmi).
  - `Sudah Ada Website Resmi`: Tempat sudah memiliki domain situs web mandiri (Target Audit / Redesign).
- **Ekstraksi Kontak Lengkap:** Mengambil nomor telepon lokal (otomatis diformat bersih), link langsung WhatsApp (`wa.me`), alamat lengkap, rating, dan jumlah ulasan.
- **Deduplikasi Cerdas:** Menghindari data ganda antar wilayah pencarian menggunakan identitas unik `cid` Google Maps.
- **Sinkronisasi Otomatis Google Sheets:** Data langsung diimpor dan diformat otomatis (freeze header row, navy styling, auto-column resize) via CLI Google Sheets (`gsheets`).
- **Tanpa Dependensi Berat:** Berjalan murni menggunakan Python Standard Library (tanpa `pip install`, tanpa Puppeteer, tanpa Playwright).

---

## Struktur Proyek

```text
├── scraper.py           # Script pencarian satuan untuk satu kata kunci/wilayah
├── batch_scrape.py      # Script batch untuk beberapa spot target + auto-sync ke Google Sheets
├── .env.example         # Template konfigurasi environment variables
├── .gitignore           # Aturan pengabaian file sensitif dan output CSV
└── README.md            # Dokumentasi proyek
```

---

## Panduan Instalasi dan Konfigurasi

### 1. Prasyarat
- Python 3.8 atau versi lebih baru.
- Akun Google di [Serper.dev](https://serper.dev) (Tersedia 2.500 pencarian gratis tanpa kartu kredit).
- Plugin / CLI `gsheets` jika ingin menggunakan fitur sinkronisasi otomatis ke Google Sheets.

### 2. Konfigurasi Environment Variables
Salin file `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Isi konfigurasi pada file `.env`:

```env
SERPER_API_KEY=api_key_serper_anda
SPREADSHEET_ID=id_spreadsheet_google_anda
```

> **Catatan:** File `.env` sudah masuk ke dalam `.gitignore` sehingga credential Anda tidak akan pernah terunggah ke repositori publik.

---

## Cara Penggunaan

### 1. Pencarian Satuan (`scraper.py`)

Gunakan untuk mencari satu wilayah tertentu secara fleksibel:

```bash
# Mencari semua tempat di wilayah tertentu
python3 scraper.py -k "API_KEY_ANDA" -q "cafe di tebet jakarta selatan"

# Hanya menyaring tempat yang BELUM memiliki website resmi
python3 scraper.py -k "API_KEY_ANDA" -q "cafe di cipete jakarta selatan" --only-prospects -o "prospek_cipete.csv"
```

### 2. Batch Scraping & Sinkronisasi ke Google Sheets (`batch_scrape.py`)

Gunakan untuk menjalankan pemindaian otomatis ke 5 spot strategis (Cipete, Tebet, Blok M, PIK, Tanjung Duren), melakukan deduplikasi, dan mengunggah langsung ke spreadsheet Google:

```bash
python3 batch_scrape.py
```

Jika ingin menjalankan batch scraping dan hanya menyimpannya ke CSV lokal tanpa mengunggah ke Google Sheets:

```bash
python3 batch_scrape.py --skip-upload -o "hasil_lokal.csv"
```

---

## Kolom Data yang Dihasilkan

| Kolom | Deskripsi |
| :--- | :--- |
| `No` | Nomor urut data |
| `Wilayah` | Label wilayah pencarian |
| `Nama_Tempat` | Nama cafe atau bisnis |
| `Kategori` | Kategori bisnis dari Google Maps |
| `Status_Website` | Klasifikasi (Belum Ada Web / Hanya Sosmed / Sudah Ada Web) |
| `Tautan_Terdaftar` | URL yang terdaftar di Google Maps |
| `No_Telepon` | Nomor telepon kontak lokal (08xx atau 021-xx) |
| `Link_WhatsApp` | Tautan langsung chat WhatsApp jika tersedia di listing |
| `Alamat_Lengkap` | Alamat fisik lengkap |
| `Rating` | Rata-rata bintang ulasan Google |
| `Jumlah_Ulasan` | Total review pelanggan |
| `Rekomendasi_Penawaran` | Strategi penawaran jasa yang disarankan |

---

## Lisensi

MIT License. Bebas digunakan dan dimodifikasi untuk kebutuhan riset bisnis dan komersial.
