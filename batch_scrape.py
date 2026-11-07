#!/usr/bin/env python3
"""
Batch Scraper Prospek Website Cafe Jakarta ke Google Sheets.
Mengambil data dari beberapa spot target strategis via Serper.dev /maps,
melakukan deduplikasi, dan menyinkronkan data bersih ke Google Sheets.
Tanpa dependensi eksternal (Python Standard Library murni).
"""

import sys
import os
import json
import csv
import argparse
import subprocess
import urllib.request
import urllib.error

TARGET_SPOTS = [
    {"wilayah": "Cipete (Jaksel)", "query": "cafe di cipete jakarta selatan"},
    {"wilayah": "Tebet (Jaksel)", "query": "cafe di tebet jakarta selatan"},
    {"wilayah": "Blok M (Jaksel)", "query": "cafe di blok m jakarta selatan"},
    {"wilayah": "PIK (Jakut)", "query": "cafe di pantai indah kapuk"},
    {"wilayah": "Tanjung Duren (Jakbar)", "query": "cafe di tanjung duren jakarta barat"}
]

NON_WEBSITE_DOMAINS = (
    "instagram.com",
    "facebook.com",
    "linktr.ee",
    "wa.me",
    "gofood.link",
    "grab.com",
    "shopee.co.id",
    "tiktok.com",
    "chope.co",
    "bit.ly"
)

def load_env_file(filepath: str = ".env"):
    """Membaca file .env sederhana tanpa dependensi python-dotenv."""
    if not os.path.isfile(filepath):
        return
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = val

def fetch_serper_maps(api_key: str, query: str, location: str = "Indonesia") -> list:
    url = "https://google.serper.dev/maps"
    payload = json.dumps({
        "q": query,
        "location": location
    }).encode("utf-8")
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("places", [])
    except Exception as err:
        print(f"[Error] Gagal scraping query '{query}': {err}", file=sys.stderr)
        return []

def clean_phone_number(raw_phone: str) -> str:
    if not raw_phone or raw_phone == "-":
        return "-"
    phone = raw_phone.strip()
    if phone.startswith("+62 "):
        return "0" + phone[4:]
    if phone.startswith("+62"):
        return "0" + phone[3:]
    if phone.startswith("+"):
        return "'" + phone
    return phone

def extract_whatsapp_link(booking_links: list) -> str:
    for link in booking_links:
        if "wa.me" in link or "whatsapp.com" in link:
            return link
    return "-"

def check_website_status(website_url: str):
    if not website_url:
        return "TIDAK_ADA", "-"
    
    clean_url = website_url.lower()
    for dom in NON_WEBSITE_DOMAINS:
        if dom in clean_url:
            return "HANYA_SOSMED_ATAU_MENU", website_url
            
    return "PUNYA_WEBSITE_RESMI", website_url

def main():
    load_env_file()
    
    parser = argparse.ArgumentParser(description="Batch Scraper Prospek Website Cafe ke Google Sheets")
    parser.add_argument("--api-key", "-k", default=os.getenv("SERPER_API_KEY"), help="API Key Serper.dev")
    parser.add_argument("--spreadsheet-id", "-s", default=os.getenv("SPREADSHEET_ID"), help="ID Spreadsheet Google Sheets")
    parser.add_argument("--output", "-o", default="prospek_5_spot_jakarta.csv", help="Path file CSV output")
    parser.add_argument("--skip-upload", action="store_true", help="Lewati proses upload ke Google Sheets")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("[Error] SERPER_API_KEY tidak ditemukan. Atur di .env atau via argumen -k.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Mulai batch scraping untuk {len(TARGET_SPOTS)} wilayah target...")
    seen_cids = set()
    all_leads = []
    
    for spot in TARGET_SPOTS:
        wilayah = spot["wilayah"]
        query = spot["query"]
        print(f"\n--> Mengambil data untuk {wilayah} ('{query}')...")
        places = fetch_serper_maps(args.api_key, query)
        print(f"    Ditemukan {len(places)} tempat dari Google Maps.")
        
        for p in places:
            cid = p.get("cid", "")
            title = p.get("title", "")
            address = p.get("address", "-")
            
            dedup_key = cid if cid else f"{title}_{address}"
            if dedup_key in seen_cids:
                continue
            seen_cids.add(dedup_key)
            
            raw_web = (p.get("website") or "").strip()
            phone = clean_phone_number(p.get("phoneNumber", "-"))
            booking_links = p.get("bookingLinks", [])
            wa_link = extract_whatsapp_link(booking_links)
            category = p.get("type", p.get("category", "Cafe"))
            rating = p.get("rating", "-")
            reviews = p.get("ratingCount", 0)
            
            status, web_link = check_website_status(raw_web)
            
            if status == "TIDAK_ADA":
                status_desc = "Belum Ada Website"
                rekomendasi = "PROSPEK TINGGI: Buat Website Profil & Menu"
            elif status == "HANYA_SOSMED_ATAU_MENU":
                status_desc = "Hanya Sosmed / Menu Digital"
                rekomendasi = "PROSPEK SEDANG: Upgrade Sosmed ke Website Resmi"
            else:
                status_desc = "Sudah Ada Website Resmi"
                rekomendasi = "PROSPEK RENDAH: Tawaran Redesign / Maintenance"
                
            all_leads.append({
                "Wilayah": wilayah,
                "Nama_Tempat": title,
                "Kategori": category,
                "Status_Website": status_desc,
                "Tautan_Terdaftar": web_link,
                "No_Telepon": phone,
                "Link_WhatsApp": wa_link,
                "Alamat_Lengkap": address,
                "Rating": rating,
                "Jumlah_Ulasan": reviews,
                "Rekomendasi_Penawaran": rekomendasi
            })
            
    print(f"\nTotal prospek terkumpul (setelah deduplikasi): {len(all_leads)} tempat.")
    
    numbered_leads = []
    for idx, lead in enumerate(all_leads, 1):
        row = {"No": idx}
        row.update(lead)
        numbered_leads.append(row)
        
    keys = numbered_leads[0].keys()
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(numbered_leads)
        
    print(f"Data disimpan ke CSV: {args.output}")
    
    if args.skip_upload:
        print("[Info] Unggah ke Google Sheets dilewati (--skip-upload aktif).")
        return
        
    if not args.spreadsheet_id:
        print("[Perhatian] SPREADSHEET_ID tidak disetel. Lewati unggah ke Google Sheets.")
        print("Tentukan via -s <ID> atau di file .env.")
        return
        
    print(f"\nMengunggah data ke Google Sheets (ID: {args.spreadsheet_id})...")
    res = subprocess.run([
        "gsheets", "mutate", "import-csv", args.spreadsheet_id, args.output, "--sheet", "Sheet1"
    ], capture_output=True, text=True)
    
    if res.returncode == 0:
        print("[Sukses] Data berhasil diunggah ke Google Sheets!")
        # Terapkan styling otomatis
        subprocess.run(["gsheets", "mutate", "freeze", args.spreadsheet_id, "--sheet-id", "0", "--rows", "1"], capture_output=True)
        subprocess.run([
            "gsheets", "mutate", "format", args.spreadsheet_id,
            "--sheet-id", "0", "--start-row", "0", "--end-row", "1",
            "--start-col", "0", "--end-col", "12",
            "--bold", "--align", "CENTER", "--bg-color", "#1B365D", "--fg-color", "#FFFFFF"
        ], capture_output=True)
        subprocess.run(["gsheets", "mutate", "autosize", args.spreadsheet_id, "--sheet-id", "0", "--start-col", "0", "--end-col", "12"], capture_output=True)
    else:
        print(f"[Error] Gagal unggah ke Sheets: {res.stderr}")

if __name__ == "__main__":
    main()
