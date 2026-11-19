# Traveloka Kereta Scraper v1.1
import asyncio
import json
import random
import os
import re
import sys
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

# ── import model (sesuaikan path jika perlu) ─────────────────────────────────
try:
    from models import TransportSegment
except ImportError:
    # Fallback: definisi minimal agar scraper bisa jalan standalone
    from dataclasses import dataclass
    from typing import Optional
    @dataclass
    class TransportSegment:
        id: str
        mode: str
        provider: str
        provider_code: Optional[str]
        origin: str
        destination: str
        departure_time: datetime
        arrival_time: datetime
        duration_minutes: int
        price: float
        seat_class: Optional[str]
        available_seats: Optional[int]
        rating: Optional[float]

CONFIG = {
    "headless": False,
    "timeout": 90000,
    "output_json": "hasil_kereta_traveloka.json",
}

# ── helpers ───────────────────────────────────────────────────────────────────

async def human_delay(min_sec=1.5, max_sec=4.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def gentle_human_behavior(page):
    await page.mouse.move(random.randint(100, 800), random.randint(100, 500), steps=10)
    await human_delay(1.0, 2.5)
    for _ in range(random.randint(2, 3)):
        await page.mouse.wheel(0, random.randint(100, 300))
        await human_delay(0.8, 1.8)
    await human_delay(1.5, 3.0)

def parse_price(raw: str) -> float:
    """'Rp 410.000' → 410000.0"""
    cleaned = re.sub(r'[Rp\s.,]', '', raw)
    # titik sebagai pemisah ribuan: '410000' setelah strip semua non-digit
    digits = re.sub(r'\D', '', cleaned)
    return float(digits) if digits else 0.0

def map_seat_class(kelas_raw: str) -> str:
    """'Eksekutif (AC)' → 'Executive', dst."""
    kelas_lower = kelas_raw.lower()
    if "eksekutif" in kelas_lower or "executive" in kelas_lower:
        return "Executive"
    if "bisnis" in kelas_lower or "business" in kelas_lower:
        return "Business"
    if "ekonomi" in kelas_lower or "economy" in kelas_lower:
        return "Economy"
    return kelas_raw  # kembalikan apa adanya jika tidak dikenali

def build_datetime(tanggal: str, jam: str) -> datetime:
    """
    Gabungkan tanggal + jam jadi datetime.
    Jika jam tiba < jam berangkat, asumsikan tiba keesokan harinya.
    """
    return datetime.strptime(f"{tanggal} {jam}", "%Y-%m-%d %H:%M")

def calc_duration(dep: datetime, arr: datetime) -> int:
    """Durasi dalam menit; tangani kasus overnight (arr < dep)."""
    if arr < dep:
        arr += timedelta(days=1)
    return int((arr - dep).total_seconds() / 60)

def segment_id(index: int) -> str:
    return f"SEG-{index:03d}"

# ── scraper utama ─────────────────────────────────────────────────────────────

async def scrape_traveloka_v11() -> list:
    print("\n" + "=" * 85)
    print("   TRAVELOKA KERETA SCRAPER v11 - OUTPUT TransportSegment")
    print("=" * 85)

    asal      = input("Kode stasiun ASAL     : ").strip().upper()
    tujuan    = input("Kode stasiun TUJUAN   : ").strip().upper()
    tanggal   = input("Tanggal (YYYY-MM-DD)  : ").strip()
    num_adult = input("Jumlah dewasa         : ").strip() or "1"

    segments: list[TransportSegment] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=CONFIG["headless"],
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/134.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        page = await context.new_page()

        try:
            dt_obj = datetime.strptime(tanggal, "%Y-%m-%d")
            dt_str = f"{dt_obj.day}-{dt_obj.month}-{dt_obj.year}.null"
            url = (
                f"https://www.traveloka.com/id-id/kereta-api/search"
                f"?st={asal}.{tujuan}&dt={dt_str}&ps={num_adult}.0&pd=KAI"
            )

            print(f"\nURL: {url}")
            await page.goto(url, timeout=CONFIG["timeout"], wait_until="networkidle")
            await gentle_human_behavior(page)

            print("Menunggu hasil kereta...")
            await page.wait_for_selector("text=Pilih", timeout=40000)

            cards = await page.locator("div:has-text('Pilih')").all()
            print(f"Ditemukan {len(cards)} raw cards (sebelum filter)")

            seen        = set()
            seg_counter = 1

            for i, card in enumerate(cards):
                try:
                    full_text = await card.inner_text()

                    # ── Filter 1: buang header/toolbar ────────────────────────
                    if "URUTKAN" in full_text or full_text.count("Waktu") > 1:
                        continue

                    # ── Parsing ───────────────────────────────────────────────
                    nama_match = re.search(r'([A-Za-z\s]+?\s*\(\d+[A-Z]*\))', full_text)
                    nama = nama_match.group(1).strip() if nama_match else None
                    if not nama:
                        continue  # skip card tanpa nama kereta

                    kelas_match = re.search(
                        r'(Eksekutif|Ekonomi|Bisnis)\s*\(([A-Z]+)\)', full_text
                    )
                    kelas_raw = (
                        f"{kelas_match.group(1)} ({kelas_match.group(2)})"
                        if kelas_match else ""
                    )

                    times = re.findall(r'\b\d{2}:\d{2}\b', full_text)
                    if len(times) < 2:
                        continue  # skip card tanpa jam lengkap
                    jam_bgkt = times[0]
                    jam_tiba = times[1]

                    harga_match = re.search(r'Rp\s?[\d.,]+', full_text)
                    if not harga_match:
                        continue  # skip card tanpa harga
                    harga_float = parse_price(harga_match.group(0))

                    # ── Filter 2: deduplikasi ─────────────────────────────────
                    dedup_key = (nama, kelas_raw, jam_bgkt, jam_tiba, harga_float)
                    if dedup_key in seen:
                        continue
                    seen.add(dedup_key)

                    # ── Bangun datetime & durasi ──────────────────────────────
                    dep_dt  = build_datetime(tanggal, jam_bgkt)
                    arr_dt  = build_datetime(tanggal, jam_tiba)
                    durasi  = calc_duration(dep_dt, arr_dt)
                    # sesuaikan arr_dt jika overnight
                    if arr_dt < dep_dt:
                        arr_dt += timedelta(days=1)

                    # ── Buat TransportSegment ─────────────────────────────────
                    seg = TransportSegment(
                        id               = segment_id(seg_counter),
                        mode             = "train",
                        provider         = nama,
                        provider_code    = None,
                        origin           = asal,
                        destination      = tujuan,
                        departure_time   = dep_dt,
                        arrival_time     = arr_dt,
                        duration_minutes = durasi,
                        price            = harga_float,
                        seat_class       = map_seat_class(kelas_raw) if kelas_raw else None,
                        available_seats  = None,
                        rating           = None,
                    )
                    segments.append(seg)
                    seg_counter += 1

                    print(
                        f"   [{seg.id}] {seg.provider} | {seg.seat_class} "
                        f"| {jam_bgkt} → {jam_tiba} ({seg.duration_str}) "
                        f"| {seg.price_str}"
                    )

                except Exception as e:
                    print(f"   [SKIP] Card {i+1} gagal diekstrak: {e}")
                    continue

            print(f"\nTotal TransportSegment valid: {len(segments)}")

            # ── Simpan JSON (serialisasi manual datetime → string) ────────────
            def seg_to_dict(s: TransportSegment) -> dict:
                return {
                    "id":               s.id,
                    "mode":             s.mode,
                    "provider":         s.provider,
                    "provider_code":    s.provider_code,
                    "origin":           s.origin,
                    "destination":      s.destination,
                    "departure_time":   s.departure_time.isoformat(),
                    "arrival_time":     s.arrival_time.isoformat(),
                    "duration_minutes": s.duration_minutes,
                    "price":            s.price,
                    "seat_class":       s.seat_class,
                    "available_seats":  s.available_seats,
                    "rating":           s.rating,
                }

            # Auto-append ke file JSON yang sudah ada
            existing = []
            if os.path.exists(CONFIG["output_json"]):
                with open(CONFIG["output_json"], "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        existing = json.loads(content)

            all_data = existing + [seg_to_dict(s) for s in segments]
            with open(CONFIG["output_json"], "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)

            print(f"Disimpan ke '{CONFIG['output_json']}' (total: {len(all_data)} entri)")

        except Exception as e:
            print(f"ERROR: {e}")
            await page.screenshot(path="traveloka_error.png")
            print("Screenshot disimpan → traveloka_error.png")
        finally:
            input("\nTekan ENTER untuk tutup browser...")
            await browser.close()

    return segments  # kembalikan list[TransportSegment] untuk integrasi


if __name__ == "__main__":
    result = asyncio.run(scrape_traveloka_v11())
    print(f"\n[DONE] Mengembalikan {len(result)} TransportSegment object")