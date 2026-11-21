import gdb, struct
gdb.execute("set pagination off")
inf = gdb.selected_inferior()
def q(a):
    try: return struct.unpack("<Q", bytes(inf.read_memory(a, 8)))[0]
    except Exception: return None
def dump(name, a, n):
    print("--- %s @ 0x%x" % (name, a))
    for i in range(0, n, 16):
        x, y = q(a + i), q(a + i + 8)
        print("  +0x%03x: %s %s" % (i, "?" if x is None else "0x%016x" % x, "?" if y is None else "0x%016x" % y))
found = False
def rets_probe(rsp):
    for n in (0x8000, 0x4000, 0x2000, 0x1000, 0x400):
        try:
            b = bytes(inf.read_memory(rsp, n))
            return [(rsp + i, struct.unpack_from("<Q", b, i)[0]) for i in range(0, n, 8)]
        except Exception: pass
    return []
for th in inf.threads():
    th.switch()
    rsp = int(gdb.parse_and_eval("$rsp"))
    pr = []
    pr.append("=== %s rsp=0x%x r14=0x%x rip=0x%x" % (th.name, rsp, int(gdb.parse_and_eval("$r14")), int(gdb.parse_and_eval("$rip"))))
    if not any(v == 0x26b11aa for _, v in rets_probe(rsp)): continue
    print(pr[0])
    rets = []
    for off in range(0, 0x8000, 8):
        v = q(rsp + off)
        if v is None: break
        if 0x400000 <= v < 0x754d000: rets.append((rsp + off, v))
    for slot, v in rets[:40]: print("  stack 0x%x -> 0x%x" % (slot, v))
    for slot, v in rets:
        if v == 0x26b11aa:
            found = True
            query = q(slot - 0x30)
            print("query (saved rbx) = 0x%x" % query)
            dump("query", query, 0x80)
            fence = q(query + 0x38)
            res = q(query + 0x28)
            if fence:
                dump("fence", fence, 0x100)
                vt = q(fence)
                if vt and 0x400000 <= vt < 0xc000000: dump("fence vtable", vt, 0x100)
                for k in range(0, 0x100, 8):
                    p = q(fence + k)
                    if p and 0x100000000 <= p < 0x10000000000 and p != fence:
                        dump("fence+0x%x target" % k, p, 0x40)
            if res: dump("result slots", res, 0x100)
            break
if not found: print("no 0x26b11aa frame on the render thread")
