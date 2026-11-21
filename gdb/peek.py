import ctypes, ctypes.wintypes as w, struct, sys
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = w.HANDLE
k32.ReadProcessMemory.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
h = k32.OpenProcess(0x0410, False, int(sys.argv[1]))
def q(a):
    buf = ctypes.create_string_buffer(8); got = ctypes.c_size_t()
    return struct.unpack("<Q", buf.raw)[0] if k32.ReadProcessMemory(h, ctypes.c_void_p(a), buf, 8, ctypes.byref(got)) else None
for spec in sys.argv[2:]:
    a, before, after = [int(x, 16) for x in spec.split(":")]
    print("=== 0x%x" % a)
    for off in range(-before, after, 8):
        v = q(a + off)
        tag = ""
        if v and 0x7550000 <= v < 0xc000000:
            s0 = q(v)
            if s0 and 0x400000 <= s0 < 0x754d000: tag = "  <- vtable? slots %s" % " ".join("%x" % (q(v + 8 * i) or 0) for i in range(6))
        elif v and 0x400000 <= v < 0x754d000: tag = "  <- code"
        print("  %+5x %s%s" % (off, "?" if v is None else "%016x" % v, tag))
