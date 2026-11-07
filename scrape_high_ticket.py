#!/usr/bin/env python3
"""
Scraper Prospek Bisnis Jasa Bernilai Tinggi (High-Ticket Services) ke Google Sheets.
Mencakup: Klinik Gigi, Klinik Kecantikan, Auto Detailing, Desain Interior, Pet Hotel, dan Wedding Organizer.
"""

import sys
import os
import json
import csv
import subprocess
import urllib.request
import urllib.error

HIGH_TICKET_TARGETS = [
    {"industri": "Klinik Gigi", "query": "klinik gigi di jakarta selatan"},
    {"industri": "Klinik Kecantikan", "query": "klinik kecantikan di pantai indah kapuk"},
    {"industri": "Auto Detailing & PPF", "query": "auto detailing di jakarta barat"},
    {"industri": "Desain Interior", "query": "desain interior di jakarta selatan"},
    {"industri": "Pet Hotel & Grooming", "query": "pet hotel di jakarta selatan"},
    {"industri": "Wedding Organizer", "query": "wedding organizer jakarta selatan"}
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
    api_key = os.getenv("SERPER_API_KEY", "8c0b536fe83cc2d33e2cefadf965307721c0231d")
    spreadsheet_id = os.getenv("SPREADSHEET_ID", "1vNjP5BnHxgzB7K_u_ILuiETbFJRgKy1DH4q3880Uihk")
    target_sheet = "Jasa_Bernilai_Tinggi"
    sheet_id_num = "910512603"
    output_csv = "/Users/user/.gemini/antigravity/scratch/maps-lead-scraper/prospek_jasa_bernilai_tinggi.csv"
    
    print(f"Mulai scraping {len(HIGH_TICKET_TARGETS)} ceruk bisnis jasa bernilai tinggi...")
    seen_cids = set()
    all_leads = []
    
    for target in HIGH_TICKET_TARGETS:
        industri = target["industri"]
        query = target["query"]
        print(f"\n--> Mengambil data ceruk: {industri} ('{query}')...")
        places = fetch_serper_maps(api_key, query)
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
            category = p.get("type", p.get("category", industri))
            rating = p.get("rating", "-")
            reviews = p.get("ratingCount", 0)
            
            status, web_link = check_website_status(raw_web)
            
            if status == "TIDAK_ADA":
                status_desc = "Belum Ada Website"
                rekomendasi = "PROSPEK TINGGI: Buat Website Profil & Booking Reservasi"
            elif status == "HANYA_SOSMED_ATAU_MENU":
                status_desc = "Hanya Sosmed / Menu Digital"
                rekomendasi = "PROSPEK SEDANG: Upgrade Sosmed ke Website Portofolio Resmi"
            else:
                status_desc = "Sudah Ada Website Resmi"
                rekomendasi = "PROSPEK RENDAH: Tawaran Redesign / Audit Kecepatan"
                
            all_leads.append({
                "Industri": industri,
                "Nama_Bisnis": title,
                "Kategori_Maps": category,
                "Status_Website": status_desc,
                "Tautan_Terdaftar": web_link,
                "No_Telepon": phone,
                "Link_WhatsApp": wa_link,
                "Alamat_Lengkap": address,
                "Rating": rating,
                "Jumlah_Ulasan": reviews,
                "Rekomendasi_Penawaran": rekomendasi
            })
            
    print(f"\nTotal prospek terkumpul (setelah deduplikasi): {len(all_leads)} bisnis.")
    
    numbered_leads = []
    for idx, lead in enumerate(all_leads, 1):
        row = {"No": idx}
        row.update(lead)
        numbered_leads.append(row)
        
    keys = numbered_leads[0].keys()
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(numbered_leads)
        
    print(f"Data disimpan ke CSV: {output_csv}")
    
    print(f"\nMengunggah data ke Google Sheets tab '{target_sheet}'...")
    res = subprocess.run([
        "gsheets", "mutate", "import-csv", spreadsheet_id, output_csv, "--sheet", target_sheet
    ], capture_output=True, text=True)
    
    if res.returncode == 0:
        print("[Sukses] Data berhasil diunggah ke Google Sheets!")
        # Styling tab
        subprocess.run(["gsheets", "mutate", "freeze", spreadsheet_id, "--sheet-id", sheet_id_num, "--rows", "1"], capture_output=True)
        subprocess.run([
            "gsheets", "mutate", "format", spreadsheet_id,
            "--sheet-id", sheet_id_num, "--start-row", "0", "--end-row", "1",
            "--start-col", "0", "--end-col", "12",
            "--bold", "--align", "CENTER", "--bg-color", "#0F4C81", "--fg-color", "#FFFFFF"
        ], capture_output=True)
        subprocess.run(["gsheets", "mutate", "autosize", spreadsheet_id, "--sheet-id", sheet_id_num, "--start-col", "0", "--end-col", "12"], capture_output=True)
    else:
        print(f"[Error] Gagal unggah ke Sheets: {res.stderr}")

if __name__ == "__main__":
    main()
