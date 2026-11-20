# tree-sitter-filter (Tugas 4 dan 5)

Grammar tree-sitter untuk DSL filter di halaman admin, contohnya:

```
status in ("open", "pending") and priority >= 2 or not archived = true and title contains "spam"
```

## Isi folder

| Path | Isi |
| --- | --- |
| `grammar.js` | Definisi grammar (satu-satunya file yang ditulis manual) |
| `test/corpus/dasar.txt` | 10 kasus uji |
| `queries/highlights.scm` | Query untuk syntax highlighting |
| `contoh.filter` | File contoh untuk `tree-sitter parse` dan `tree-sitter highlight` |
| `catatan/` | Bukti kendala: conflict saat `or` tanpa `prec`, dan error `module.exports` |
| `src/` | Parser hasil `tree-sitter generate`, jangan diedit |

## Menjalankan tes (Tugas 4)

Dari folder ini:

```bash
tree-sitter generate
tree-sitter test
```

Hasil yang diharapkan: `Total parses: 10; successful parses: 10; failed parses: 0`.

Catatan: `tree-sitter init` versi 0.27 membuat `package.json` dengan `"type": "module"`, jadi
grammar harus ditulis `export default grammar({...})`. Bentuk `module.exports = grammar({...})`
dari materi menghasilkan error (lihat `catatan/module-exports-error.txt`).

## Menjalankan highlight (Tugas 5)

1. Jalankan `tree-sitter init-config` sekali. Perintah ini membuat `~/.config/tree-sitter/config.json`.
2. Buka file itu, lalu isi `parser-directories` dengan folder **induk** dari folder ini.
   Contoh kalau repo ada di `~/tree-sitter`:
   ```json
   "parser-directories": ["/home/NAMA_USER/tree-sitter"]
   ```
3. Di file yang sama, ubah warna `number` di bagian `theme`:
   ```json
   "number": { "bold": true, "color": 166 },
   ```
   Di tema bawaan, `number` dan `constant.builtin` sama-sama memakai warna 94, sehingga angka `2`
   dan boolean `true` tampil dengan warna yang sama. Setelah diubah, angka jadi oranye (166) dan
   boolean tetap cokelat (94).
4. Jalankan dari folder mana saja:
   ```bash
   tree-sitter highlight tree-sitter-filter/contoh.filter
   ```

Pemetaan warna setelah langkah 3:

| Token | Capture | Warna (kode 256 warna) |
| --- | --- | --- |
| `and` `or` `not` `in` `contains` | `@keyword` | 56 (ungu) |
| `=` `!=` `>` `<` `>=` `<=` | `@operator` | 239 (abu-abu, tebal) |
| string | `@string` | 28 (hijau) |
| angka | `@number` | 166 (oranye, tebal) |
| `true` `false` | `@constant.builtin` | 94 (cokelat, tebal) |
| nama field | `@property` | 124 (merah) |
