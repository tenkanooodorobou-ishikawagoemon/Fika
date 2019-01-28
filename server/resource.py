# coding: utf-8
import psutil

mem = psutil.virtual_memory()

print("MEM_TOTAL: {0}".format(mem.total))
print("MEM_USED: {0}".format(mem.used))
print("MEM_AVAILABLE: {0}".format(mem.available))
