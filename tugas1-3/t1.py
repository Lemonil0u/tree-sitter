import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

# Potongan 1: Fungsi
kode_fungsi = b"""def sapa(nama):
    return nama
"""
tree1 = parser.parse(kode_fungsi)
print("=== POHON FUNGSI ===")
print(tree1.root_node)


# Cek node bernama vs anonim (termasuk di dalam parameters)
for c in tree1.root_node.children[0].children:
    print(c.type, "bernama" if c.is_named else "anonim")
    if c.type == "parameters":
        for anak_param in c.children:
            print(anak_param.type, "bernama" if anak_param.is_named else "anonim")

fn_node = tree1.root_node.children[0]
print("Jumlah children:", len(fn_node.children), [c.type for c in fn_node.children])
print("Jumlah named_children:", len(fn_node.named_children), [c.type for c in fn_node.named_children])

# Potongan 2: If/Else
kode_if = b"""if x > 0:
    y = 1
else:
    y = 0
"""
tree2 = parser.parse(kode_if)
print("\n=== POHON IF/ELSE ===")
print(tree2.root_node)

# Potongan 3: Class
kode_class = b"""class Mobil:
    def jalan(self):
        return True
"""
tree3 = parser.parse(kode_class)
print("\n=== POHON CLASS ===")
print(tree3.root_node)

# Simulasi kode rusak (error)
kode_rusak = b"""def sapa(nama)
    return nama
"""
tree_rusak = parser.parse(kode_rusak)
print("\n=== POHON ERROR ===")
print(tree_rusak.root_node)