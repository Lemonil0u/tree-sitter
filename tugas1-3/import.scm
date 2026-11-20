; import os                -> import_statement berisi dotted_name
(import_statement
  name: (dotted_name) @modul)

; import datetime as dt    -> dotted_name dibungkus aliased_import
(import_statement
  name: (aliased_import
    name: (dotted_name) @modul))

; from pathlib import Path -> nama modul ada di field module_name
(import_from_statement
  module_name: (_) @modul)
