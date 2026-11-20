"""Program kecil pencatat tiket helpdesk.

Dipakai sebagai file uji untuk Tugas 2 (jelajah.py) dan Tugas 3 (query).
"""

import os
import json
import datetime as dt
from pathlib import Path
from collections import Counter, defaultdict

FILE_DATA = Path("tiket.json")
STATUS_VALID = ("open", "pending", "closed")


class Tiket:
    """Satu tiket helpdesk."""

    def __init__(self, nomor, judul, prioritas=1):
        self.nomor = nomor
        self.judul = judul
        self.prioritas = prioritas
        self.status = "open"
        self.dibuat = dt.datetime.now()

    def tutup(self):
        self.status = "closed"

    def ke_dict(self):
        return {
            "nomor": self.nomor,
            "judul": self.judul,
            "prioritas": self.prioritas,
            "status": self.status,
            "dibuat": self.dibuat.isoformat(),
        }


def muat_tiket(path):
    """Membaca daftar tiket dari file JSON."""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    hasil = []
    for item in data:
        t = Tiket(item["nomor"], item["judul"], item["prioritas"])
        t.status = item["status"]
        hasil.append(t)
    return hasil


def simpan_tiket(path, daftar):
    with open(path, "w") as f:
        json.dump([t.ke_dict() for t in daftar], f, indent=2)


def tambah_tiket(daftar, judul, prioritas=1):
    nomor = len(daftar) + 1
    tiket = Tiket(nomor, judul, prioritas)
    daftar.append(tiket)
    print("Tiket baru:", nomor, judul)
    return tiket


def cari_tiket(daftar, kata_kunci, status=None, prioritas_min=0):
    hasil = []
    for t in daftar:
        if kata_kunci.lower() not in t.judul.lower():
            continue
        if status is not None and t.status != status:
            continue
        if t.prioritas < prioritas_min:
            continue
        hasil.append(t)
    return hasil


def ringkasan(daftar):
    # print di dalam komentar ini tidak boleh ikut terhitung: print("x")
    per_status = Counter(t.status for t in daftar)
    per_prioritas = defaultdict(list)
    for t in daftar:
        per_prioritas[t.prioritas].append(t.nomor)
    pesan = "gunakan print() untuk debug"  # string ini juga bukan pemanggilan
    return per_status, per_prioritas, pesan


def tampilkan(daftar):
    if not daftar:
        print("Belum ada tiket.")
        return
    for t in daftar:
        print(f"#{t.nomor} [{t.status}] P{t.prioritas} {t.judul}")


def main():
    daftar = muat_tiket(FILE_DATA)
    tambah_tiket(daftar, "Printer lantai 2 macet", 2)
    tambah_tiket(daftar, "Reset password email", 1)
    tambah_tiket(daftar, "Server invoice down", 3)
    daftar[0].tutup()
    tampilkan(daftar)
    per_status, _, _ = ringkasan(daftar)
    print("Ringkasan:", dict(per_status))
    simpan_tiket(FILE_DATA, daftar)


if __name__ == "__main__":
    main()
