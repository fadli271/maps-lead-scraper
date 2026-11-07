# Maps Lead Scraper & Google Sheets Sync

Alat otomasi berbasis Python untuk mengekstrak, memfilter, dan mengklasifikasikan prospek bisnis lokal dari Google Maps ke Google Sheets secara real-time.

Dapat digunakan untuk berbagai industri dan ceruk bisnis:
- **F&B:** Cafe, Restoran, Coffee Shop.
- **Kesehatan & Estetika:** Klinik Gigi, Klinik Kecantikan, Skincare.
- **Otomotif:** Auto Detailing, Workshop Modifikasi, Paint Protection Film (PPF).
- **Properti & Jasa Rumah:** Desain Interior, Kontraktor Renovasi, Arsitek.
- **Layanan Hewan:** Pet Hotel, Grooming, Klinik Hewan.
- **Event & Pernikahan:** Wedding Organizer, Studio Foto.

---

## Fitur Utama

- **Integrasi Google Maps:** Mengambil data tempat bisnis lokal via endpoint `/maps` Serper.dev tanpa risiko pemblokiran IP atau CAPTCHA.
- **Deteksi Otomatis Status Website:**
  - `Belum Ada Website`: Bisnis tidak mencantumkan tautan apapun di Google Maps (Target Utama Pembuatan Web Baru).
  - `Hanya Sosmed / Menu Digital`: Bisnis hanya mencantumkan Instagram, Linktree, TikTok, atau GoFood (Target Upgrade ke Website Resmi).
  - `Sudah Ada Website Resmi`: Bisnis sudah memiliki domain web mandiri (Target Audit / Redesign / Maintenance).
- **Ekstraksi Kontak Lengkap:** Mengambil nomor telepon lokal (otomatis diformat bersih ke `08xx`/`021-xx`), link langsung WhatsApp (`wa.me`), alamat lengkap, rating, dan jumlah ulasan.
- **Deduplikasi Cerdas:** Menghindari data ganda antar wilayah pencarian menggunakan identitas unik `cid` Google Maps.
- **Sinkronisasi Otomatis Google Sheets:** Data langsung diimpor dan diformat otomatis (freeze header row, navy styling, auto-column resize) via CLI Google Sheets (`gsheets`).
- **Tanpa Dependensi Berat:** Berjalan murni menggunakan Python Standard Library (tanpa `pip install`, tanpa headless browser).

---

## Struktur Repositori

```text
├── scraper.py           # Script pencarian satuan untuk satu kata kunci/wilayah
├── batch_scrape.py      # Script batch untuk beberapa target spot + auto-sync ke Google Sheets
├── .env.example         # Template konfigurasi environment variables
├── .gitignore           # Aturan pengabaian file sensitif dan output CSV lokal
└── README.md            # Dokumentasi proyek
```

---

## Panduan Instalasi dan Konfigurasi

### 1. Prasyarat
- Python 3.8 atau versi lebih baru.
- Akun di [Serper.dev](https://serper.dev) (Tersedia 2.500 pencarian gratis tanpa kartu kredit).
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

> **Keamanan:** File `.env` sudah masuk ke dalam `.gitignore` sehingga credential Anda tidak akan pernah terunggah ke repositori publik.

---

## Cara Penggunaan

### 1. Pencarian Satuan (`scraper.py`)

Gunakan untuk mencari satu ceruk bisnis di wilayah tertentu:

```bash
# Contoh 1: Mencari klinik gigi di Jakarta Selatan
python3 scraper.py -k "API_KEY_ANDA" -q "klinik gigi di jakarta selatan" --only-prospects -o "prospek_klinik_gigi.csv"

# Contoh 2: Mencari auto detailing di Jakarta Barat
python3 scraper.py -k "API_KEY_ANDA" -q "auto detailing di jakarta barat" --only-prospects -o "prospek_detailing.csv"

# Contoh 3: Mencari cafe di Tebet
python3 scraper.py -k "API_KEY_ANDA" -q "cafe di tebet jakarta selatan" --only-prospects -o "prospek_cafe_tebet.csv"
```

### 2. Batch Scraping & Sinkronisasi ke Google Sheets (`batch_scrape.py`)

Gunakan untuk menjalankan pemindaian otomatis ke beberapa target spot, melakukan deduplikasi, dan mengunggah langsung ke spreadsheet Google:

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
| `Nama_Tempat` | Nama bisnis atau tempat |
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
