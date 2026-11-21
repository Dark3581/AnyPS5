# Scripts behind #24525 (Star Wars Jedi: Survivor, PPSA07783)

Throwaway investigation scripts, not meant for `main`. Set `RUN` (the relinked title folder), `ANYPS5` (an AnyPS5 checkout with `build/`) and `SCRIPTS` (this folder). The guest addresses (`0x26b11aa`, `0x201a870000`) are specific to PPSA07783 01.000.013.

- `gdb/q.py`: finds threads whose stack holds the occlusion-query wait (`0x26b11aa`), and dumps the query, its task-graph event and the result slots.
- `gdb/q2.py`: the guest frames of every thread, plus the events the waiters share.
- `gdb/rt.py`: registers and stack of the render and RHI threads.
- `gdb/scanptr.py PID HEX...`: scans all committed memory of a live process (`ReadProcessMemory`) for 64-bit values, skipping query objects.
- `gdb/peek.py PID ADDR:BEFORE:AFTER...`: reads qwords around addresses, and marks code and vtable pointers.
- `boot/multiboot.sh N...`: boots the title several times. After each stop it waits until the queue-0 worker leaves `nvgpucomp64.dll`, then lists the large pipeline builds.
- `boot/snapshots.sh N`: takes a `q2.py` snapshot every 15 s, and scans for the owner of the event once the same event is stuck in two snapshots.
- `boot/capture2.sh N...`: captures pipelines of 2 M words or more with `APS5_DUMP_COMPUTE_PIPELINES`, for replay with `agc_compute_pipeline_replay`.
- `spirv/mutate.py SRC DST nocontraction|switch1`: rewrites a capture (strips `NoContraction` decorations, or cuts every `OpSwitch` to its first case), for compile-time experiments.
- `spirv/canon.py A B`: compares opcode counts of two captures.
- `spirv/spvstat.py MODULE.spv`: words per opcode, and the largest functions.
- `ghidra/DecompileAt.java OUT ADDR...`: headless Ghidra post-script that disassembles, creates and decompiles functions at the given addresses (`analyzeHeadless <proj> jedi -import jedi.exe -noanalysis -postScript DecompileAt.java out.c 0x26b0f80`).
