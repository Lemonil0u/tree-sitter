# Tugas 3 - Nama fungsi dan jumlah parameternya (versi matches)
# Cara pakai: python q_fungsi.py <file.py> fungsi.scm
# Pakai matches() karena butuh PASANGAN @nama dan @params dari fungsi yang sama.

import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2]).read()
tree = parser.parse(kode)

# matches(): list of (indeks_pola, {nama_capture: [node]}), satu entri per fungsi
for _, cap in QueryCursor(Query(PY, pola)).matches(tree.root_node):
    nama = cap["nama"][0]
    params = cap["params"][0]
    # named_child_count: jumlah anak bernama di dalam ( ), jadi ( , ) tidak ikut terhitung
    jumlah = params.named_child_count
    print(f"baris {nama.start_point[0] + 1}: {nama.text.decode()}{params.text.decode()} -> {jumlah} parameter")
