import gdb, struct, collections
gdb.execute("set pagination off")
inf = gdb.selected_inferior()
def q(a):
    try: return struct.unpack("<Q", bytes(inf.read_memory(a, 8)))[0]
    except Exception: return None
def stack(rsp):
    for n in (0x8000, 0x4000, 0x2000, 0x1000, 0x400):
        try:
            b = bytes(inf.read_memory(rsp, n))
            return [(rsp + i, struct.unpack_from("<Q", b, i)[0]) for i in range(0, n, 8)]
        except Exception: pass
    return []
def guest(v): return 0x400000 <= v < 0x754d000
events = collections.Counter()
frames = {}
for th in inf.threads():
    th.switch()
    rsp = int(gdb.parse_and_eval("$rsp"))
    words = stack(rsp)
    rets = [(s, v) for s, v in words if guest(v)]
    frames[th.name or str(th.num)] = [v for _, v in rets[:12]]
    for slot, v in rets:
        if v == 0x26b11aa:
            query = q(slot - 0x30)
            ev = q(query + 0x38) if query else None
            if ev: events[ev] += 1
            break
print("waiting events:", {hex(k): v for k, v in events.items()})
for name, rs in sorted(frames.items()):
    print("%-28s %s" % (name, " ".join("%x" % r for r in rs)))
for ev in events:
    print("--- event 0x%x" % ev)
    for k in range(0, 0x60, 8): print("  +0x%02x %s" % (k, "?" if q(ev + k) is None else "%016x" % q(ev + k)))
    node = q(ev); seen = 0
    while node and seen < 40 and 0x100000000 <= node < 0x10000000000:
        row = [q(node + k) for k in range(0, 0x20, 8)]
        print("  node 0x%x: %s" % (node, " ".join("?" if x is None else "%x" % x for x in row)))
        for x in row[1:]:
            if x and 0x100000000 <= x < 0x10000000000:
                vt = q(x)
                if vt and guest(vt): print("     obj 0x%x vtable 0x%x slots %s" % (x, vt, " ".join("%x" % (q(vt + 8 * i) or 0) for i in range(6))))
        node = row[0]; seen += 1
