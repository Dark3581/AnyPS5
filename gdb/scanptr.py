import ctypes, ctypes.wintypes as w, struct, sys

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p), ("AllocationProtect", w.DWORD),
                ("PartitionId", w.WORD), ("RegionSize", ctypes.c_size_t), ("State", w.DWORD), ("Protect", w.DWORD), ("Type", w.DWORD)]

k32.OpenProcess.restype = w.HANDLE
k32.VirtualQueryEx.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.ReadProcessMemory.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

pid = int(sys.argv[1])
targets = {int(a, 16) for a in sys.argv[2:]}
h = k32.OpenProcess(0x0410, False, pid)
if not h: sys.exit("OpenProcess failed %d" % ctypes.get_last_error())

def read(addr, n):
    buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t()
    if not k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)): return None
    return buf.raw[:got.value]

def q(a):
    b = read(a, 8)
    return struct.unpack("<Q", b)[0] if b and len(b) == 8 else None

def guest_code(v): return 0x400000 <= v < 0x754d000

pats = {t: struct.pack("<Q", t) for t in targets}
addr, hits, scanned = 0, [], 0
mbi = MBI()
while addr < 0x7fffffff0000 and k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
    base, size = mbi.BaseAddress or 0, mbi.RegionSize
    readable = mbi.State == 0x1000 and not (mbi.Protect & 0x101) and mbi.Protect != 0x1 and mbi.Protect != 0
    if readable:
        for off in range(0, size, 1 << 24):
            n = min(1 << 24, size - off)
            b = read(base + off, n)
            if not b: continue
            scanned += len(b)
            for t, p in pats.items():
                i = b.find(p)
                while i >= 0:
                    if i % 8 == 0: hits.append((t, base + off + i))
                    i = b.find(p, i + 1)
    addr = base + size
print("scanned %.1f GiB, %d hits" % (scanned / 2**30, len(hits)))
hits = [(t, a) for t, a in hits if q(a - 0x38) != 0x9d8c918]
print("non-query hits", len(hits))
for t, a in hits[:80]:
    vt = None
    for back in range(0, 0x200, 8):
        v = q(a - back)
        if v and 0x7550000 <= v < 0xc000000:
            s0 = q(v)
            if s0 and guest_code(s0): vt = (a - back, v, [q(v + 8 * i) for i in range(8)]); break
    row = [q(a - 0x30 + 8 * k) for k in range(10)]
    print("0x%x -> 0x%x  around: %s" % (a, t, " ".join("?" if x is None else "%x" % x for x in row)))
    if vt: print("    object 0x%x (+0x%x) vtable 0x%x: %s" % (vt[0], a - vt[0], vt[1], " ".join("%x" % (x or 0) for x in vt[2])))
