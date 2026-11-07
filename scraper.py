#!/usr/bin/env python3
"""
Google Maps Cafe Lead Scraper & Filter via Serper.dev /maps
Mendeteksi cafe di Google Maps yang belum memiliki website resmi.
Tanpa dependensi eksternal (Python Standard Library murni).
"""

import sys
import os
import json
import csv
import argparse
import urllib.request
import urllib.error

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
    except urllib.error.HTTPError as err:
        print(f"[Error] HTTP {err.code}: {err.reason}", file=sys.stderr)
        return []
    except Exception as err:
        print(f"[Error] Gagal menghubungi Serper: {err}", file=sys.stderr)
        return []

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

def process_places(places: list) -> list:
    results = []
    
    for place in places:
        name = place.get("title", "Tanpa Nama")
        address = place.get("address", "-")
        phone = place.get("phoneNumber", "-")
        raw_web = (place.get("website") or "").strip()
        rating = place.get("rating", "-")
        reviews = place.get("ratingCount", 0)
        category = place.get("type", place.get("category", "Cafe"))
        
        booking_links = place.get("bookingLinks", [])
        wa_link = extract_whatsapp_link(booking_links)
        
        status, web_link = check_website_status(raw_web)
        
        is_prospect = status in ("TIDAK_ADA", "HANYA_SOSMED_ATAU_MENU")
        
        if status == "TIDAK_ADA":
            status_desc = "Belum Ada Website"
            action = "PROSPEK: BUAT WEBSITE BARU"
        elif status == "HANYA_SOSMED_ATAU_MENU":
            status_desc = "Hanya Pakai Sosmed / Menu Digital"
            action = "PROSPEK: UPGRADE KE WEBSITE RESMI"
        else:
            status_desc = "Sudah Ada Website Resmi"
            action = "PROSPEK: AUDIT ATAU MAINTENANCE"
            
        results.append({
            "Nama": name,
            "Kategori": category,
            "Status_Web": status_desc,
            "Tautan_Terdaftar": web_link,
            "No_Telepon": phone,
            "Link_WhatsApp": wa_link,
            "Alamat": address,
            "Rating": rating,
            "Jumlah_Ulasan": reviews,
            "Aksi_Pitch": action,
            "Is_Prospect": is_prospect
        })
        
    return results

def save_to_csv(results: list, filename: str):
    if not results:
        print("Tidak ada data untuk disimpan.")
        return
    
    # Buang flag internal sebelum diekspor
    export_data = []
    for r in results:
        clean_row = {k: v for k, v in r.items() if k != "Is_Prospect"}
        export_data.append(clean_row)
        
    keys = export_data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(export_data)
    print(f"[Selesai] Berhasil menyimpan {len(export_data)} data ke: {filename}")

def main():
    parser = argparse.ArgumentParser(description="Filter Prospek Website Cafe via Serper.dev /maps")
    parser.add_argument("--query", "-q", default="cafe di cipete jakarta selatan", help="Kata kunci pencarian")
    parser.add_argument("--api-key", "-k", default=os.getenv("SERPER_API_KEY"), help="API Key Serper.dev")
    parser.add_argument("--output", "-o", default="prospek_cafe.csv", help="Nama file CSV output")
    parser.add_argument("--only-prospects", action="store_true", help="Hanya simpan tempat yang belum punya website resmi")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("[Error] Masukkan API key via -k atau atur SERPER_API_KEY.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Mengambil data Google Maps untuk query: '{args.query}'...")
    places = fetch_serper_maps(args.api_key, args.query)
    
    if not places:
        print("Tidak ada tempat ditemukan.")
        return
        
    leads = process_places(places)
    
    if args.only_prospects:
        leads = [l for l in leads if l["Is_Prospect"]]
        print(f"Menyaring hanya tempat prospek (tanpa web resmi): {len(leads)} dari {len(places)} tempat.")
        
    save_to_csv(leads, args.output)

if __name__ == "__main__":
    main()
