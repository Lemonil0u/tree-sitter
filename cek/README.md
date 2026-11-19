# CLI Pendeteksi TODO, Fungsi Panjang, dan Syntax Error (`cek.py`)

Alat analisis statis berbasis `tree-sitter` dan `tree-sitter-python` untuk memindai seluruh file Python (`.py`) secara rekursif di dalam suatu direktori dan melaporkan:
1. **Komentar Tugas (`[TODO]`):** Komentar yang mengandung kata kunci `TODO` atau `FIXME`.
2. **Fungsi Panjang (`[PANJANG]`):** Definisi fungsi (`function_definition`) yang panjangnya lebih dari 30 baris, mencakup fungsi tingkat atas, *method* di dalam kelas, maupun fungsi bersarang.
3. **Kesalahan Sintaks (`[ERROR]`):** File yang memiliki pohon sintaks bermasalah (`has_error == True`) beserta nomor baris pertama dan jenis error (`ERROR` atau `MISSING`).

---

## Cara Memasang Dependensi

Pastikan Python 3.10+ sudah terpasang, lalu instal pustaka yang dibutuhkan:

```bash
pip install tree-sitter tree-sitter-python
```

---

## Cara Menjalankan

Jalankan skrip dari direktori utama proyek dengan menyertakan *path* folder target sebagai argumen:

```bash
python cek/cek.py <path_folder_target>
```

### Contoh Penggunaan

1. **Menguji pada folder kasus uji (`cek/uji`):**
   ```bash
   python cek/cek.py cek/uji
   ```

2. **Memindai kode proyek nyata (`docs`):**
   ```bash
   python cek/cek.py docs
   ```

*(Catatan: Direktori lingkungan dan metadata seperti `.venv`, `venv`, `.git`, `node_modules`, dan `__pycache__` otomatis dilewati saat pemindaian).*

---

## Contoh Output

Hasil eksekusi pada folder uji (`cek/uji`):

```text
[ERROR]   cek/uji/tes_error.py:1: ditemukan syntax error (ERROR)
[PANJANG] cek/uji/tes_panjang.py:1: fungsi 'fungsi_panjang' (34 baris)
[TODO]    cek/uji/tes_todo.py:2: # TODO: rapikan kode ini
```

Hasil eksekusi pada file proyek nyata (`docs/scraper_v1.1.py`):

```text
[PANJANG] docs/scraper_v1.1.py:89: fungsi 'scrape_traveloka_v11' (171 baris)
```

---

## Cara Kerja Singkat

* **Query S-Expression (`QueryCursor`):** Menggunakan pola `((comment) @c (#match? @c "TODO|FIXME"))` untuk mengekstrak komentar dan `(function_definition name: (identifier) @nama) @fungsi` untuk menghitung rentang baris (`end_point[0] - start_point[0] + 1`).
* **Penelusuran Pohon Error (*DFS Traversal*):** Memeriksa properti `tree.root_node.has_error`, lalu menelusuri *child node* secara rekursif untuk menemukan node pertama dengan status `is_error` atau `is_missing`.