import gdb
gdb.execute("set pagination off")
def run(c):
    try: gdb.execute(c)
    except Exception as e: print("ERR", c, e)
for inf in gdb.inferiors():
    ths = sorted(inf.threads(), key=lambda t: 0 if (t.name or "").startswith("RenderThread") else 1)
    for th in ths:
        if th.name and any(k in th.name for k in ("RHIThread","RHIFrameFlip","RHIFrameOffset","AgcViewport","RenderThread")):
            th.switch()
            print("=== %s" % th.name)
            run("info registers")
            run("x/12i $rip")
            run("x/512gx $rsp")
