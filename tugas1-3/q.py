# Tugas 3 - Penjalan query (versi captures)
# Cara pakai: python q.py <file.py> <pola.scm>
# Cukup ganti file .scm untuk mencoba query lain, kode Python tidak perlu diubah.

import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2]).read()
tree = parser.parse(kode)

# captures(): hasilnya dict {nama_capture: [node, node, ...]}
hasil = QueryCursor(Query(PY, pola)).captures(tree.root_node)
for nama, nodes in hasil.items():
    # diurutkan per posisi supaya mudah dicocokkan dengan hitungan manual
    for n in sorted(nodes, key=lambda n: n.start_byte):
        print(f"@{nama}  baris {n.start_point[0] + 1}: {n.text.decode()}")
